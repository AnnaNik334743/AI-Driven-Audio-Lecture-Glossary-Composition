from typing import Callable, Optional
from fastapi import APIRouter
import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline

from llm_service.app.api.utils import *
from llm_service.app.api.prompts import RUSSIAN_USER_PROMPT, ENGLISH_USER_PROMPT
from llm_service.app.config import HF_MODEL_NAME

HF_PIPELINE_OBJ: Optional[Callable] = None


def load_model() -> Optional[Callable]:
    try:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

        model = AutoModelForCausalLM.from_pretrained(
            HF_MODEL_NAME,
            quantization_config=bnb_config,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
        )

        tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME)

        pipeline_obj = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )

        return pipeline_obj

    except Exception as e:
        print("Something is wrong with loading the model! " + str(e))
        return None


def init_hf_pipeline_obj():
    global HF_PIPELINE_OBJ
    HF_PIPELINE_OBJ = load_model()


self_hosted_llm = APIRouter(on_startup=[init_hf_pipeline_obj])


def wrap_message_as_prompt(message: str) -> str:  # обертка для промпта, см. карточку модели HF_MODEL_NAME
    return f"GPT4 Correct User: {message}<|end_of_turn|>GPT4 Correct Assistant: "


def post_process_generated_text(text: str) -> str:
    return text.split('GPT4 Correct Assistant:')[-1]


def generate_answer(prompt: str) -> str:
    if HF_PIPELINE_OBJ is not None:
        sequences = HF_PIPELINE_OBJ(
            prompt,
            do_sample=True,
            max_new_tokens=2048,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            num_return_sequences=1,
        )
        post_processed = post_process_generated_text(sequences[0]['generated_text'])
        return post_processed
    return ""


@self_hosted_llm.post("/create_glossary")
async def create_glossary_with_self_hosted_llm(text: str,
                                               prompt_language: Language | None = None) -> Glossary:

    text_pieces = await split_text_if_it_is_too_long(text)
    all_glossary_parts = []

    for text_piece in text_pieces:

        if prompt_language is None:
            prompt_language = await detect_language(text)

        if prompt_language == Language.ru:
            message = f"{RUSSIAN_USER_PROMPT} <text>{text_piece}</text>"
        else:
            message = f"{ENGLISH_USER_PROMPT} <text>{text_piece}</text>"

        prompt = wrap_message_as_prompt(message)
        content = generate_answer(prompt)

        print(content)

        glossary_parts = await turn_str_to_glossary_parts(content)
        all_glossary_parts.extend(glossary_parts)

    glossary = await turn_glossary_parts_to_glossary(all_glossary_parts)

    return glossary

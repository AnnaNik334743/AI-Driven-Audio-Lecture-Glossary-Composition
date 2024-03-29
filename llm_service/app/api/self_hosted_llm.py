from typing import Callable, Optional
from fastapi import APIRouter
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline

from llm_service.app.api.utils import *
from llm_service.app.api.prompts import PROMPTS
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
            quantization_config=bnb_config if torch.cuda.is_available() else None,
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


async def wrap_message_as_prompt(message: str) -> str:  # обертка для промпта, см. карточку модели HF_MODEL_NAME
    return f"GPT4 Correct User: {message}<|end_of_turn|>GPT4 Correct Assistant: "


async def post_process_generated_text(text: str) -> str:
    return text.split('GPT4 Correct Assistant:')[-1]


async def generate_answer(prompt: str) -> str:
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
        post_processed = await post_process_generated_text(sequences[0]['generated_text'])
        return post_processed
    return ""


@self_hosted_llm.post("/create_glossary_parts")
async def create_glossary_parts_with_self_hosted_llm(text: str,
                                                     prompt_language: Language | None = None) -> list[GlossaryItem]:
    prompt_language = await detect_language(text, pre_detected=prompt_language)

    text_pieces = await split_text_if_it_is_too_long(text)
    all_glossary_parts = []

    for text_piece in text_pieces:

        message = f"{PROMPTS[prompt_language.value]['user']} <text>{text_piece}</text>"
        prompt = await wrap_message_as_prompt(message)

        try:
            content = await generate_answer(prompt)
        except Exception:  # There could be many reasons, especially maximum sequence length
            content = ""

        print(content)

        glossary_parts = await turn_str_to_glossary_parts(content)
        all_glossary_parts.extend(glossary_parts)

    return all_glossary_parts


@self_hosted_llm.post("/create_full_glossary_from_parts")
async def create_glossary_from_parts_with_self_hosted_llm(all_glossary_parts: list[GlossaryItem]) -> Glossary:
    all_glossary_parts = await post_process(all_glossary_parts)
    glossary = await turn_glossary_parts_to_glossary(all_glossary_parts)
    return glossary


@self_hosted_llm.post("/create_full_glossary_from_text")
async def create_glossary_with_self_hosted_llm(text: str, prompt_language: Language | None = None) -> Glossary:
    all_glossary_parts = await create_glossary_parts_with_self_hosted_llm(text=text, prompt_language=prompt_language)
    all_glossary_parts = await post_process(all_glossary_parts)
    glossary = await create_glossary_from_parts_with_self_hosted_llm(all_glossary_parts)
    return glossary

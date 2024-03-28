from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from api.schema import *
from api.utils import *
from api.prompts import PROMPTS
from config import OPENAI_CLIENT, OPENAI_MODEL_NAME
from dotenv import load_dotenv

load_dotenv()

chat_gpt = APIRouter()


@chat_gpt.post("/create_glossary_parts")
async def create_glossary_parts_with_self_hosted_llm(text: Text,
                                                     prompt_language: Language | None = None):
    text = text.text
    prompt_language = await detect_language(text, pre_detected=prompt_language)
    text_pieces = await split_text_if_it_is_too_long(text)

    async def generate_parts(text_pieces: list[str], prompt_language: Language) -> str:
        for text_piece in text_pieces:
            d = {"messages": [{"role": "system", "content": f"{PROMPTS[prompt_language.value]['system']}"},
                              {"role": "user",
                               "content": f"{PROMPTS[prompt_language.value]['user']} <text>{text_piece}</text>"}]}

            response = OPENAI_CLIENT.chat.completions.create(
                model=OPENAI_MODEL_NAME,
                messages=d['messages']
            )

            content = response.choices[0].message.content
            print(content)
            glossary_parts = await turn_str_to_glossary_parts(content)
            yield '\n'.join([str(gp) for gp in glossary_parts]) + '\n'

    return StreamingResponse(generate_parts(text_pieces, prompt_language), media_type="text/plain")


@chat_gpt.post("/create_full_glossary_from_parts")
async def create_glossary_from_parts_with_chat_gpt(all_glossary_parts: list[GlossaryItem]) -> Glossary:
    all_glossary_parts = await post_process(all_glossary_parts)
    glossary = await turn_glossary_parts_to_glossary(all_glossary_parts)
    return glossary


@chat_gpt.post("/create_full_glossary_from_text")
async def create_glossary_with_chat_gpt(text: str, prompt_language: Language | None = None) -> Glossary:
    all_glossary_parts = await create_glossary_parts_with_chat_gpt(text=text, prompt_language=prompt_language)
    all_glossary_parts = await post_process(all_glossary_parts)
    glossary = await create_glossary_from_parts_with_chat_gpt(all_glossary_parts)
    return glossary

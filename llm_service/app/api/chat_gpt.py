from fastapi import APIRouter
from llm_service.app.api.utils import *
from llm_service.app.api.prompts import PROMPTS
from llm_service.app.config import OPENAI_CLIENT, OPENAI_MODEL_NAME

chat_gpt = APIRouter()


@chat_gpt.post("/create_glossary_parts")
async def create_glossary_parts_with_chat_gpt(text: str,
                                              prompt_language: Language | None = None) -> list[GlossaryItem]:
    prompt_language = await detect_language(text, pre_detected=prompt_language)

    text_pieces = await split_text_if_it_is_too_long(text)
    all_glossary_parts = []

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
        all_glossary_parts.extend(glossary_parts)

    return all_glossary_parts


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

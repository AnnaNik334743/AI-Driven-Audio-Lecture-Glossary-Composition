from fastapi import APIRouter
from llm_service.app.api.utils import *
from llm_service.app.api.prompts import RUSSIAN_SYSTEM_PROMPT, ENGLISH_SYSTEM_PROMPT, RUSSIAN_USER_PROMPT, \
    ENGLISH_USER_PROMPT
from llm_service.app.config import OPENAI_CLIENT, OPENAI_MODEL_NAME

chat_gpt = APIRouter()


@chat_gpt.post("/create_glossary")
async def create_glossary_with_chat_gpt(text: str,
                                        prompt_language: Language | None = None) -> Glossary:

    text_pieces = await split_text_if_it_is_too_long(text)
    all_glossary_parts = []

    for text_piece in text_pieces:

        if prompt_language is None:
            prompt_language = await detect_language(text)

        if prompt_language == Language.ru:
            d = {"messages": [{"role": "system", "content": f"{RUSSIAN_SYSTEM_PROMPT}"},
                              {"role": "user", "content": f"{RUSSIAN_USER_PROMPT} <text>{text_piece}</text>"}]}
        else:
            d = {"messages": [{"role": "system", "content": f"{ENGLISH_SYSTEM_PROMPT}"},
                              {"role": "user", "content": f"{ENGLISH_USER_PROMPT} <text>{text_piece}</text>"}]}

        response = OPENAI_CLIENT.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=d['messages']
        )

        content = response.choices[0].message.content

        print(content)

        glossary_parts = await turn_str_to_glossary_parts(content)
        all_glossary_parts.extend(glossary_parts)

    glossary = await turn_glossary_parts_to_glossary(all_glossary_parts)

    return glossary

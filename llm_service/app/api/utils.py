import re
import langdetect
from enum import Enum
from llm_service.app.api.schema import GlossaryItem, Glossary


class Language(Enum):
    ru = 'ru'
    en = 'en'


async def detect_language(text: str) -> Language:
    lang = langdetect.detect(text)
    return Language(lang)


async def turn_str_to_glossary_parts(glossary_parts: str,
                                     remove_too_long_terms: bool = True,
                                     too_long_terms_n_words: int = 5) -> list[GlossaryItem] | str:
    glossary_parts = re.sub('```', '', re.sub('```json', '', glossary_parts)).strip()
    glossary_parts = re.sub('определение', 'definition', re.sub('термин', 'term', glossary_parts))

    if glossary_parts[0] != '[':
        glossary_parts = '[' + glossary_parts
    if glossary_parts[-1] != ']':
        glossary_parts = glossary_parts + ']'

    try:
        glossary_parts_list = eval(glossary_parts)

        glossary_items_list = []
        for part in glossary_parts_list:
            vals = list(part.values())

            if not remove_too_long_terms or remove_too_long_terms and len(vals[0].split()) <= too_long_terms_n_words:
                glossary_items_list.append(GlossaryItem(term=vals[0], definition=vals[1]))

        return glossary_items_list

    except Exception:
        return glossary_parts


async def turn_glossary_parts_to_glossary(glossary_parts: list[GlossaryItem] | str) -> Glossary | str:
    try:
        return Glossary(glossary=glossary_parts)
    except Exception:
        return str({'glossary': glossary_parts})

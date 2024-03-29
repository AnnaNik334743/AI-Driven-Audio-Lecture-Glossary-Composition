import re
import langdetect
from enum import Enum
from llm_service.app.api.schema import GlossaryItem, Glossary


class Language(Enum):
    ru = 'ru'
    en = 'en'


async def detect_language(text: str, pre_detected: str | None) -> Language:
    try:
        return Language(pre_detected)
    except Exception as e:
        try:
            lang = langdetect.detect(text)
            return Language(lang)
        except Exception as e:
            return Language('en')


async def split_list_into_sublists(lst: list, n: int, overlap_length: int = 0) -> list:
    sublists = []
    i = 0
    while i < len(lst):
        sublist = lst[i:i + n]
        sublists.append(sublist)
        if i + n >= len(lst):
            break
        i += n - overlap_length
    return sublists


async def split_text_if_it_is_too_long(text: str, chunk_size_in_words: int = 512, overlap: int = 0) -> list[str]:
    words = text.split()  # you can change it to a better tokenizer (or segmenter) if needed
    return [' '.join(subwords) for subwords in await split_list_into_sublists(words, chunk_size_in_words, overlap)]


async def turn_str_to_glossary_parts(glossary_parts: str,
                                     remove_too_long_terms: bool = True,
                                     too_long_terms_n_words: int = 5) -> list[GlossaryItem]:
    glossary_parts = re.sub('```', '', re.sub('```json', '', glossary_parts)).strip()
    glossary_parts = re.sub('определение', 'definition', re.sub('термин', 'term', glossary_parts))

    if len(glossary_parts):
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
        return []


async def turn_glossary_parts_to_glossary(glossary_parts: list[GlossaryItem]) -> Glossary:
    try:
        return Glossary(glossary=glossary_parts)
    except Exception:
        return Glossary(glossary=[])


async def post_process(glossary_parts: list[GlossaryItem], n: int = 2):
    # удалить термины, если их названия дублируются и они находятся в рамках какого-то окна
    final_list = []
    for part in glossary_parts:
        if part.term.lower() not in [val.term.lower() for val in final_list[max(0, -n):]]:
            final_list.append(part)
    return final_list

from pydantic import BaseModel


class Text(BaseModel):
    """
    {'text': ''}
    """
    text: str


class GlossaryItem(BaseModel):
    """
    {'term': '', 'definition': ''}
    """
    term: str
    definition: str


class Glossary(BaseModel):
    """
    {
    'glossary': [
        {'term': '', 'definition': ''},
        {'term': '', 'definition': ''},
        ...
        ]
    }
    """
    glossary: list[GlossaryItem]

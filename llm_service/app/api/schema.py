from pydantic import BaseModel


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

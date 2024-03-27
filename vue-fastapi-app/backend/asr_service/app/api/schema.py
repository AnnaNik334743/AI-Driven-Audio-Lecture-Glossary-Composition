from pydantic import BaseModel


class Text(BaseModel):
    """
    {'text': ''}
    """
    text: str


class Transcript(BaseModel):
    """
    {'transcript': ''}
    """
    transcript: str

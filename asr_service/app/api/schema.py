from pydantic import BaseModel


class Transcript(BaseModel):
    """
    {'transcript': ''}
    """
    transcript: str

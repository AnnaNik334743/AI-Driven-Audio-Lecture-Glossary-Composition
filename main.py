# Tutorial on building microservices - https://dev.to/paurakhsharma/microservice-in-python-using-fastapi-24cc
from enum import Enum
import requests
from fastapi import FastAPI

app = FastAPI()


class LLM(Enum):
    chat_gpt = 'chat_gpt'
    self_hosted_llm = 'self_hosted_llm'


async def transcribe(youtube_link: str) -> str:
    transcription = requests.post('http://127.0.0.1:8001/api/asr/transcribe_file',
                                  params={'youtube_link': youtube_link}).json()
    return transcription['transcript']


async def compose_glossary(text: str, llm_type: LLM) -> dict:
    try:
        all_glossary_parts = requests.post(f'http://127.0.0.1:8002/api/{llm_type.value}/create_glossary_parts',
                                           params={'text': text}).json()
        glossary = requests.post(f'http://127.0.0.1:8002/api/{llm_type.value}/create_full_glossary_from_parts',
                                 json=all_glossary_parts).json()
    except Exception as e:
        glossary = {'message': 'We are sorry, something has gone wrong :(', 'error': e}
    return glossary


@app.post("/get_glossary")
async def get_glossary(youtube_link: str, llm_type: LLM) -> dict:
    transcription = await transcribe(youtube_link)
    glossary = await compose_glossary(transcription, llm_type)
    return glossary


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

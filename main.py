# Tutorial on building microservices - https://dev.to/paurakhsharma/microservice-in-python-using-fastapi-24cc
from enum import Enum
import requests
from fastapi import FastAPI

app = FastAPI()


class LLM(Enum):
    chat_gpt = 'chat_gpt'
    self_hosted = 'self_hosted'


async def transcribe(youtube_link: str) -> str:
    transcribation = requests.post('http://127.0.0.1:8001/api/asr/transcribe_file',
                         params={'youtube_link': youtube_link}).json()
    return transcribation['transcript']


async def compose_glossary(text: str, llm_type: LLM) -> dict:
    try:
        if llm_type == LLM.chat_gpt:
            glossary = requests.post('http://127.0.0.1:8002/api/chat_gpt/create_glossary',
                                     params={'text': text}).json()
        else:
            glossary = requests.post('http://127.0.0.1:8002/api/self_hosted_llm/create_glossary',
                                     params={'text': text}).json()
    except Exception as e:
        glossary = {'message': 'We are sorry, something has gone wrong :(', 'error': e}
    return glossary


@app.post("/get_glossary")
async def get_glossary(youtube_link: str, llm_type: LLM) -> dict:
    transcribation = await transcribe(youtube_link)
    glossary = await compose_glossary(transcribation, llm_type)
    return glossary


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

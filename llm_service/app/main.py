from fastapi import FastAPI

from llm_service.app.api.chat_gpt import chat_gpt
from llm_service.app.api.self_hosted_llm import self_hosted_llm
from config import HOST, PORT

app = FastAPI(openapi_url="/api/llm/openapi.json", docs_url="/api/llm/docs")

app.include_router(chat_gpt, prefix='/api/chat_gpt', tags=['chat_gpt'])
app.include_router(self_hosted_llm, prefix='/api/self_hosted_llm', tags=['self_hosted_llm'])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=int(PORT))

from fastapi import FastAPI

from api.asr import asr  # app for docker
from config import HOST, PORT

app = FastAPI(openapi_url="/api/asr/openapi.json", docs_url="/api/asr/docs")

app.include_router(asr, prefix='/api/asr', tags=['asr'])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=int(PORT))

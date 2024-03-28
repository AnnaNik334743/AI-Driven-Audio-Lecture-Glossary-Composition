from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.asr import asr
from config import HOST, PORT

app = FastAPI(openapi_url="/api/asr/openapi.json", docs_url="/api/asr/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # местонахождение фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(asr, prefix='/api/asr', tags=['asr'])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=int(PORT))

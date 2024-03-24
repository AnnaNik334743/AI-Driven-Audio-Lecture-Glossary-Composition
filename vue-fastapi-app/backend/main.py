import asyncio
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  #
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Text(BaseModel):
    text: str


@app.post("/process_link/")
async def process_link(text: Text):
    async def generate_chunks():
        # Mockup for streaming text chunks
        texts = ["Chunk 11", "Chunk 21", "Chunk 31"]
        for text in texts:
            yield text.encode()
            await asyncio.sleep(1)

    return StreamingResponse(generate_chunks(), media_type="text/plain")


@app.post("/upload_file/")
async def upload_file(file: UploadFile = File(...)):
    async def generate_chunks():
        # Mockup for streaming text chunks
        texts = ["Chunk 12", "Chunk 22", "Chunk 32"]
        for text in texts:
            yield text.encode()
            await asyncio.sleep(1)

    return StreamingResponse(generate_chunks(), media_type="text/plain")


@app.post("/generate_text_chunks/")
async def generate_text_chunks(text: Text):
    async def generate_letter_chunks(text: str):
        yield (text + 'hello ').encode()
        await asyncio.sleep(2)
    return StreamingResponse(generate_letter_chunks(text.text), media_type="text/plain")


@app.post("/generate_file_from_text/")
async def generate_file_from_text(text: Text):
    filename = "text_file.txt"
    with open(filename, "w") as file:
        file.write(text.text)
    return FileResponse(filename)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8001)

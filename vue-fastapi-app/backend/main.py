import asyncio
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # местонахождение фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Text(BaseModel):  # без подобной валидации данных вы получите 422 Error при прокидывании строки с фронта
    text: str


@app.post("/process_link/")
async def process_link(text: Text):
    # здесь будет логика для скачивания аудиодорожки по ссылке из text

    async def generate_chunks():
        # здесь аудио по чанкам будет транскрибироваться ИИ-моделью и возвращаться текстовыми чанками
        chunks = ["кусочек_1_по_ссылке\n", "кусочек_2_по_ссылке\n", "кусочек_3_по_ссылке\n", "кусочек_4_по_ссылке\n"]
        for chunk in chunks:
            yield chunk.encode()  # функция - генератор
            await asyncio.sleep(0.5)  # имитация скорости, с которой обрабатывается каждый кусочек.
            # asyncio.sleep() не блокирует выполнение функции в отличие от time.sleep()

    return StreamingResponse(generate_chunks(), media_type="text/plain")  # ответ возвращается текстовыми чанками


@app.post("/upload_file/")
async def upload_file(file: UploadFile = File(...)):
    # здесь будет логика для сохранения и дальнейшей обработки файла

    async def generate_chunks():
        # здесь аудио по чанкам будет транскрибироваться ИИ-моделью и возвращаться текстовыми чанками
        chunks = ["кусочек_1_из_файла\n", "кусочек_2_из_файла\n", "кусочек_3_из_файла\n", "кусочек_4_из_файла\n"]
        for chunk in chunks:
            yield chunk.encode()  # функция - генератор
            await asyncio.sleep(0.5)  # имитация скорости, с которой обрабатывается каждый кусочек.
            # asyncio.sleep() не блокирует выполнение функции в отличие от time.sleep()

    return StreamingResponse(generate_chunks(), media_type="text/plain")  # ответ возвращается текстовыми чанками


@app.post("/generate_text_chunks/")
async def generate_text_chunks(text: Text):
    # имитация работы LLM - приходящий на вход текст каким-то образом обрабатывается
    # исходим из предположения, что LLM всегда будет генерировать текст последовательно

    async def generate_letter_chunks(letters: str):
        for letter in letters:
            yield (letter + ' ' if letter != '\n' else letter).encode()  # функция - генератор
            await asyncio.sleep(0.05)  # имитация скорости, с которой обрабатывается каждый кусочек

    return StreamingResponse(generate_letter_chunks(text.text), media_type="text/plain")  # ответ возвращается текстовыми чанками


@app.post("/generate_file_from_text/")
async def generate_file_from_text(text: Text):
    # просто функция, записывающая текст в файл и возвращающая его на фронт
    filename = "text_file.txt"
    with open(filename, "w", encoding='utf-8') as file:
        file.write(text.text)
    return FileResponse(filename)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8001)  # у меня какие-то проблемы с 8000 портом, поэтому так

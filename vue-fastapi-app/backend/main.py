import asyncio
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from asr_service.app.api.asr_utils import transcribe_audio_by_chunks, download_and_convert_audio
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline, WhisperProcessor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # местонахождение фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_whisper():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model_id = "openai/whisper-large-v3"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.config.forced_decoder_ids = WhisperProcessor.get_decoder_prompt_ids(language="russian", task="transcribe")
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    whisper_pipeline = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=256,
        chunk_length_s=30,
        batch_size=16,
        return_timestamps=True,
        torch_dtype=torch_dtype,
        device=device,
        generate_kwargs={"task":"transcribe", "language":"russian"}

    )

    return whisper_pipeline


whisper_pipeline = load_whisper()


class Text(BaseModel):  # без подобной валидации данных вы получите 422 Error при прокидывании строки с фронта
    text: str


@app.post("/process_link/")
async def process_link(text: Text):
    # здесь будет логика для скачивания аудиодорожки по ссылке из text

    youtube_link = text.text

    if not youtube_link.startswith("https://www.youtube.com/"):
        raise HTTPException(status_code=400, detail="Некорректная ссылка")

    try:
        download_and_convert_audio(youtube_link, output_name="lecture.mp3")
        return StreamingResponse(
            transcribe_audio_by_chunks(whisper_pipeline, input_file="lecture.mp3", chunk_duration=30), media_type="text/plain")
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


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

    uvicorn.run(app, host="localhost", port=8003)  # у меня какие-то проблемы с 8000 портом, поэтому так

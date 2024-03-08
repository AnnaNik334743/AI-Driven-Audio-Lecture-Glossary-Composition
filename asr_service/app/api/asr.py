from typing import Dict

import whisper
from fastapi import APIRouter

from api.asr_utils import download_wav_youtube, whisper_transcribe_file

asr = APIRouter()
# should load it from config
whisper_model = whisper.load_model("small")


@asr.get("/", response_model=str)
async def index():
    return "ASR version"


@asr.post("/transcribe_file", response_model=dict)
async def transcribe_file(youtube_link: str) -> Dict:
    download_wav_youtube(youtube_link, output_name="lecture.mp3")
    transcript = whisper_transcribe_file(whisper_model, path_to_mp3_file="lecture.mp3", delete=True)

    return {"transcript": transcript}



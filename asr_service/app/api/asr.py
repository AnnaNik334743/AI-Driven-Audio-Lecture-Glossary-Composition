import whisper
from api.asr_utils import download_and_convert_audio, whisper_transcribe_file
from api.schema import Transcript
from fastapi import APIRouter, HTTPException

asr = APIRouter()
# should load it from config
whisper_model = whisper.load_model("small")


@asr.get("/", response_model=str)
async def index():
    return "ASR version"


@asr.post("/transcribe_file", response_model=Transcript)
async def transcribe_file(youtube_link) -> Transcript:
    # Custom validation logic for YouTube link
    if not youtube_link.startswith("https://www.youtube.com/"):
        raise HTTPException(status_code=400, detail="Некорректная ссылка")

    try:
        download_and_convert_audio(youtube_link, output_name="lecture.mp3")
        transcript = whisper_transcribe_file(whisper_model, path_to_mp3_file="lecture.mp3", delete=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Transcript(transcript=transcript)

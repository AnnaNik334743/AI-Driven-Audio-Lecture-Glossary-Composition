import torch
from api.asr_utils import download_and_convert_audio, transcribe_audio_by_chunks, whisper_transcribe_file
from api.schema import Transcript
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

asr = APIRouter()

# SHOULD LOAD IT FROM CONFIG
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
model_id = "openai/whisper-small"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

whisper_pipeline = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    batch_size=16,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
)


@asr.get("/", response_model=str)
async def index():
    return "ASR version"


@asr.post("/transcribe_file", response_model=Transcript)
async def transcribe_file(youtube_link) -> Transcript:
    # youtube link validation
    if not youtube_link.startswith("https://www.youtube.com/"):
        raise HTTPException(status_code=400, detail="Некорректная ссылка")

    try:
        download_and_convert_audio(youtube_link, output_name="lecture.mp3")
        transcript = whisper_transcribe_file(whisper_pipeline, path_to_mp3_file="lecture.mp3", delete=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not transcript:
        return HTTPException(status_code=400, detail="Некорректная ссылка")

    return Transcript(transcript=transcript)


@asr.post("/transcribe_file_chunks")
async def transcribe_file_chunks(youtube_link):
    if not youtube_link.startswith("https://www.youtube.com/"):
        raise HTTPException(status_code=400, detail="Некорректная ссылка")

    try:
        download_and_convert_audio(youtube_link, output_name="lecture.mp3")
        return StreamingResponse(
            transcribe_audio_by_chunks(whisper_pipeline, input_file="lecture.mp3", chunk_duration=30))
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

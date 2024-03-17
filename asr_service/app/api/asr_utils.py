import os
import shutil

from pydub import AudioSegment
from pytube import YouTube


def download_wav_youtube(video_link, output_name="lecture.wav") -> None:
    yt = YouTube(video_link)

    video = yt.streams.filter(only_audio=True).first()
    downloaded_file = video.download()
    os.rename(downloaded_file, output_name)


def whisper_transcribe_file(model, path_to_mp3_file="lecture.wav", delete=True) -> str:
    transcription = model.transcribe(path_to_mp3_file, language="ru", verbose=False)

    print("DONE:", transcription)

    if delete:
        shutil.rmtree(path_to_mp3_file, ignore_errors=True)

    return transcription["text"]


def split_mp3_into_chunks(input_file, chunk_duration=300, chunks_dir="output_chunks"):
    os.makedirs(chunks_dir)
    audio = AudioSegment.from_file(input_file, format="mp4")

    chunk_size = chunk_duration * 1000

    for i, start_time in enumerate(range(0, len(audio), chunk_size)):
        chunk = audio[start_time:start_time + chunk_size]
        output_file = os.path.join(chunks_dir, f"chunk_{i}.mp3")
        chunk.export(output_file, format="mp3")


def transcribe_audio_by_chunks(whisper_model, input_file, chunk_duration=300, input_dir="output_chunks",
                               delete_dir=True):
    split_mp3_into_chunks(input_file, chunk_duration)

    for chunk_file in os.listdir(input_dir):
        segment = whisper_transcribe_file(whisper_model, path_to_mp3_file=os.path.join(input_dir, chunk_file))
        yield segment

    if delete_dir:
        shutil.rmtree(input_dir, ignore_errors=True)

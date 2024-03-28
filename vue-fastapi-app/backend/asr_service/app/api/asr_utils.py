import os
import shutil

from pydub import AudioSegment
from pytube import YouTube


def download_and_convert_audio(video_link, output_name="lecture.mp3") -> None:
    if os.path.exists(output_name):
        shutil.rmtree(output_name, ignore_errors=True)

    yt = YouTube(video_link)

    video = yt.streams.filter(only_audio=True).first()
    downloaded_file = video.download()

    audio = AudioSegment.from_file(downloaded_file)
    audio = audio.set_channels(1)  # Set to mono channel
    audio = audio.set_frame_rate(16000)  # Set sample rate to 16000 Hz

    audio.export(output_name, format="mp3")

    os.remove(downloaded_file)


def whisper_transcribe_file(whisper_pipeline, path_to_mp3_file="lecture.mp3", delete=True) -> str:
    result = whisper_pipeline(path_to_mp3_file)

    if delete:
        shutil.rmtree(path_to_mp3_file, ignore_errors=True)

    if len(result) > 0:
        return result['text']

    return ""


def split_mp3_into_chunks(input_file, chunk_duration=120, chunks_dir="output_chunks"):
    if os.path.exists(chunks_dir):
        shutil.rmtree(chunks_dir, ignore_errors=True)

    os.makedirs(chunks_dir)
    audio = AudioSegment.from_file(input_file, format="mp3")

    chunk_size = chunk_duration * 1000

    for i, start_time in enumerate(range(0, len(audio), chunk_size)):
        chunk = audio[start_time:start_time + chunk_size]
        output_file = os.path.join(chunks_dir, f"chunk_{i}.mp3")
        chunk.export(output_file, format="mp3")


async def transcribe_audio_by_chunks(whisper_pipeline, input_file, chunk_duration=120, input_dir="output_chunks",
                               delete_dir=True):
    split_mp3_into_chunks(input_file, chunk_duration)
    chunk_files = os.listdir(input_dir)

    for ind, chunk_file in enumerate(chunk_files):
        # # динамически удаляем предыдущие чанки
        # if ind > 0 and delete_dir:
        #     shutil.rmtree(os.path.join(input_dir, chunk_files[ind - 1]), ignore_errors=True)

        segment = whisper_transcribe_file(whisper_pipeline, path_to_mp3_file=os.path.join(input_dir, chunk_file))

        # в конце убираем всю директорию
        if ind == len(chunk_files) - 1 and delete_dir:
            shutil.rmtree(input_dir, ignore_errors=True)

        yield segment

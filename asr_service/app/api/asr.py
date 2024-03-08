from typing import List
from fastapi import APIRouter, HTTPException


asr = APIRouter()


@asr.get('/', response_model=str)
async def index():
    return "ASR version"

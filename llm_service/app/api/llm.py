from typing import List
from fastapi import APIRouter, HTTPException


llm = APIRouter()


@llm.get('/', response_model=str)
async def index():
    return "LLM version"

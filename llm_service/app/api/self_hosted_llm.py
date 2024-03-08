from fastapi import APIRouter, HTTPException


self_hosted_llm = APIRouter()


@self_hosted_llm.get('/', response_model=str)
async def index():
    return "LLM version"

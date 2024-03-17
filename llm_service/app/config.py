import os
from openai import OpenAI
from dotenv import load_dotenv
import httpx

load_dotenv()

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

HF_MODEL_NAME = os.getenv('HF_MODEL_NAME')

OPENAI_API_KEY = os.getenv('OPEN_API_KEY')
OPENAI_MODEL_NAME = os.getenv('OPENAI_MODEL_NAME')

PROXY_URL = os.environ.get('OPENAI_PROXY_URL')
PROXY_LOGIN = os.environ.get('PROXY_LOGIN')
PROXY_PASS = os.environ.get('PROXY_PASS')

OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY) if PROXY_URL is None or PROXY_URL == "" else OpenAI(
    api_key=OPENAI_API_KEY, http_client=httpx.Client(proxy=PROXY_URL))

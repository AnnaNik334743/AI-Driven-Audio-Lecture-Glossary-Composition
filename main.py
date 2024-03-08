# Tutorial on building microservices - https://dev.to/paurakhsharma/microservice-in-python-using-fastapi-24cc
import requests
from fastapi import FastAPI

app = FastAPI()


@app.get("/asr")
def feature1():
    return requests.get('http://127.0.0.1:8001/api/asr/').json()


@app.get("/llm")
def feature2():
    return requests.get('http://127.0.0.1:8002/api/llm/').json()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

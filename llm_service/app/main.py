import configparser
from fastapi import FastAPI

from api.llm import llm  # app for docker

app = FastAPI(openapi_url="/api/llm/openapi.json", docs_url="/api/llm/docs")

app.include_router(llm, prefix='/api/llm', tags=['llm'])


class MicroserviceConfig:
    def __init__(self, config_file_path):
        self.config = configparser.ConfigParser()
        self.config.read(config_file_path)

    def get_host(self, microservice_name) -> str:
        return self.config.get(microservice_name, 'host')

    def get_port(self, microservice_name) -> int:
        return int(self.config.get(microservice_name, 'port'))


if __name__ == "__main__":
    import uvicorn

    config_file_path = 'config.conf'
    microservice_config = MicroserviceConfig(config_file_path)

    microservice_name = 'LLM'

    uvicorn.run(app, host=microservice_config.get_host(microservice_name),
                port=int(microservice_config.get_port(microservice_name)))

from app.configs.base import BaseConfig


class ElasticConfig(BaseConfig):
    ELASTIC_HOST: str
    ELASTIC_PORT: int

    @property
    def ELASTIC_URL(self) -> str:
        if self.DOCKER:
            self.ELASTIC_HOST = "elasticsearch"
        return f"http://{self.ELASTIC_HOST}:{self.ELASTIC_PORT}"

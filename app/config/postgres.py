from app.config.base import BaseConfig


class PostgresConfig(BaseConfig):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_NAME: str
    POSTGRES_USER: str
    POSTGRES_PASS: str

    @property
    def DB_URL(self) -> str:
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASS}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_NAME}")


class PostgresTestConfig(BaseConfig):
    TEST_POSTGRES_HOST: str
    TEST_POSTGRES_PORT: int
    TEST_POSTGRES_NAME: str
    TEST_POSTGRES_USER: str
    TEST_POSTGRES_PASS: str

    @property
    def TEST_DB_URL(self):
        return (f"postgresql+asyncpg://{self.TEST_POSTGRES_USER}:{self.TEST_POSTGRES_PASS}@"
                f"{self.TEST_POSTGRES_HOST}:{self.TEST_POSTGRES_PORT}/{self.TEST_POSTGRES_NAME}")

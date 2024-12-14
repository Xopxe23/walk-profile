from app.config.postgres import PostgresConfig, PostgresTestConfig
from app.config.secret import SecretsConfig


class AppSettings:
    def __init__(self):
        self.postgres = PostgresConfig()
        self.test_postgres = PostgresTestConfig()
        self.secret = SecretsConfig()


settings = AppSettings()

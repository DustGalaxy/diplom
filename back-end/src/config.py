from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import dotenv_values

config = dotenv_values(".env")


class ConfigClass(BaseSettings):
    DB_HOST: str = Field(alias="DB_HOST")
    DB_PORT: str = Field(alias="DB_PORT")
    DB_PASS: str = Field(alias="DB_PASS")
    DB_USER: str = Field(alias="DB_USER")
    DB_NAME: str = Field(alias="DB_NAME")

    SESSION_LIVE_TIME: int = Field(alias="SESSION_LIVE_TIME")
    SESSION_SECRET: str = Field(alias="SESSION_SECRET")

    NATS_URL: str | None = Field(alias="NATS_URL")

    DB_URL: str = Field(default="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.DB_URL = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


Config = ConfigClass.model_validate(config)

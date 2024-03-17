from pydantic_settings import BaseSettings
from urllib.parse import quote_plus

from .jwttoken import *
from .oauth import *


class CommonSettings(BaseSettings):
    APP_NAME: str = "Blog API"
    DEBUG_MODE: bool = False


class ServerSettings(BaseSettings):
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 8000


class DatabaseSettings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def encoded_user(self):
        return quote_plus(self.DB_USER)

    @property
    def encoded_password(self):
        return quote_plus(self.DB_PASSWORD)

    @property
    def DB_URL(self):
        return f"mongodb+srv://{self.encoded_user}:{self.encoded_password}@cluster0.x8gugzz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


class Settings(CommonSettings, ServerSettings, DatabaseSettings):
    pass


settings = Settings()

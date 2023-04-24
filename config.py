from pydantic import BaseSettings, BaseModel
from injector import singleton


@singleton
class Config(BaseSettings):
    database_url: str = 'postgresql+asyncpg://admin:admin@cloud/cloud'

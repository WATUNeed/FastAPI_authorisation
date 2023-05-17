import os

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """
    Contains project settings.
    """
    db_url: str = Field(default=os.getenv('DATABASE_URL'))
    access_token_expire_min: int = Field(default=60)
    secret_key: str = Field(default=os.getenv('SECRET'))
    algorithm: str = Field(default=os.getenv('ALGORITHM'))
    redis_host: str = Field(default=os.getenv('REDIS_HOST'))
    redis_port: str = Field(default=os.getenv('REDIS_PORT'))
    request_limit: str = Field(default='100/minute')
    request_scope: str = Field(default='main')


settings = Settings()

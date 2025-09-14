import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecret")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")

    class Config:
        env_file = ".env"


settings = Settings()
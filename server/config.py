import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database URL (default fallback points to local Postgres)
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/db"
    )

    # JWT secret for signing tokens
    jwt_secret: str = os.getenv("JWT_SECRET", "supersecret")

    # GitHub token for read-only API access
    github_token: str = os.getenv("GITHUB_TOKEN", "")

    # Hugging Face integration
    hf_api_key: str = os.getenv("HF_API_KEY", "")
    hf_model: str = os.getenv("HF_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")

    class Config:
        env_file = ".env"


settings = Settings()

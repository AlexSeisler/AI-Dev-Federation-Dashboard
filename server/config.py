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

    # GitHub tokens
    github_token: str = os.getenv("GITHUB_TOKEN", "")  # Classic token
    github_fine_token: str = os.getenv("GITHUB_FINE_TOKEN", "")  # Fine-grained PAT

    # Hugging Face integration
    hf_api_key: str = os.getenv("HF_API_KEY", "")
    hf_model: str = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    hf_max_tokens: int = int(os.getenv("HF_MAX_TOKENS", "8192"))  # ✅ configurable max tokens

    class Config:
        env_file = ".env"
        extra = "ignore"  # ✅ ignore unknown env vars so startup doesn’t crash


settings = Settings()

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database URL (must come from environment — no localhost fallback in production)
    database_url: str = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("❌ DATABASE_URL is not set. Please configure it in your environment.")

    # JWT secret for signing tokens (must be set in Render or defaults to None)
    jwt_secret: str = os.getenv("JWT_SECRET")
    if not jwt_secret:
        raise ValueError("❌ JWT_SECRET is not set. Please configure it in your environment.")

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

print("✅ Config loaded")
print("DEBUG: DATABASE_URL =", settings.database_url.replace(settings.database_url.split('@')[0], "*****@"))
print("DEBUG: JWT_SECRET prefix =", settings.jwt_secret[:5] + "...")
print("DEBUG: CORS_ORIGINS (from env) =", os.getenv("CORS_ORIGINS"))

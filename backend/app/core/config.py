from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "DClaw Secure"
    app_env: str = "dev"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_secure"

    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60

    # AI provider — "openrouter" | "ollama"
    ai_provider: str = "openrouter"
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-haiku-4-5"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    model_config = ConfigDict(env_file=".env", case_sensitive=False)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

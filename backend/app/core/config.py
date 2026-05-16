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

    model_config = ConfigDict(env_file=".env", case_sensitive=False)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    secret_key: SecretStr  # in .env file we define SECRET_KEY=...
    # environment variables are automatically mapped (SECRET_KEY → secret_key)

    algorithm: str = "HS256"  # algorithm used for JWT encoding/decoding; HS256 is a common choice for symmetric keys
    access_token_expire_minutes: int = 30


settings = Settings()  # Loaded from .env file, accessible as settings.secret_key, settings.algorithm, etc.
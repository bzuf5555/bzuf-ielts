from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    telegram_bot_token: str
    groq_api_key: str
    mongodb_uri: str
    render_external_url: str = "http://localhost:8000"
    port: int = 8000
    environment: str = "development"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @field_validator("telegram_bot_token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not v or len(v) < 20:
            raise ValueError("Invalid Telegram bot token")
        return v

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def webhook_url(self) -> str:
        base = self.render_external_url.rstrip("/")
        return f"{base}/webhook"


settings = Settings()

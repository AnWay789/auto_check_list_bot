"""Конфигурация приложения через переменные окружения.

Сохраняем совместимость с текущими переменными:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- API_HOST / API_PORT
- DJANGO_API_URL / DJANGO_CALLBACK_ENDPOINT
"""

from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения."""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(default="")
    TELEGRAM_CHAT_ID: str = Field(default="")  # строкой, т.к. в Telegram бывают -100...

    # FastAPI
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8001)

    # Django API
    DJANGO_EXTERNAL_HOST: str = Field(default="http://77.244.221.86:9000")
    DJANGO_API_URL: str = Field(default="http://web:9000")
    DJANGO_CALLBACK_ENDPOINT: str = Field(default="/api/dashbord_colback/")

    class Config:
        env_file = ".env"
        case_sensitive = True

    def validate_required(self) -> None:
        """Проверяет наличие обязательных переменных окружения."""
        missing: list[str] = []
        if not self.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not self.TELEGRAM_CHAT_ID:
            missing.append("TELEGRAM_CHAT_ID")
        if not self.DJANGO_API_URL:
            missing.append("DJANGO_API_URL")
        if not self.DJANGO_CALLBACK_ENDPOINT:
            missing.append("DJANGO_CALLBACK_ENDPOINT")
        if missing:
            raise ValueError(f"Missing required env vars: {', '.join(missing)}")


settings = Settings()


"""Глобальный доступ к экземпляру aiogram Bot.

Нужно для FastAPI-роутов, когда Bot запускается в lifespan.
"""

from __future__ import annotations

from typing import Optional

from aiogram import Bot

_bot: Optional[Bot] = None


def set_bot(bot: Bot) -> None:
    global _bot
    _bot = bot


def get_bot() -> Bot:
    if _bot is None:
        raise RuntimeError("Bot is not initialized")
    return _bot


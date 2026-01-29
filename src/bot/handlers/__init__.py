"""Регистрация обработчиков Telegram бота."""

from .commands import register_command_handlers
from .callbacks import register_callback_handlers

__all__ = ["register_command_handlers", "register_callback_handlers"]


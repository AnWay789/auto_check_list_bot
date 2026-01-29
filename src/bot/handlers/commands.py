"""Командные обработчики Telegram бота."""

from __future__ import annotations

from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message


async def start_command(message: Message) -> None:
    await message.answer(
        "Привет! Я бот для автоматизированной проверки дашбордов.\n"
        "Я буду отправлять уведомления о дашбордах, которые нужно проверить."
    )


def register_command_handlers(dp: Dispatcher) -> None:
    dp.message.register(start_command, Command("start"))


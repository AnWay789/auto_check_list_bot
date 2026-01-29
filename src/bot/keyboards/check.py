"""Клавиатуры для сценария проверки дашбордов."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def dashboard_check_keyboard(event_uuid: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Все ОК!", callback_data=f"check_ok_{event_uuid}"),
                InlineKeyboardButton(text="❌ Есть проблема!", callback_data=f"check_problem_{event_uuid}"),
            ]
        ]
    )


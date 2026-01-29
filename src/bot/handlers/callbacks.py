"""Callback обработчики (inline-кнопки)."""

from __future__ import annotations

from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery

from ...services.checks_registry import ChecksRegistry


def register_callback_handlers(dp: Dispatcher, registry: ChecksRegistry) -> None:
    
    async def _handle(callback: CallbackQuery) -> None:
        await registry.handle_callback(callback)
    
    
    
    
    
    dp.callback_query.register(_handle, F.data.startswith("check_"))

    


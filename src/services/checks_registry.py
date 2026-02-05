"""Хранилище активных проверок и бизнес-логика сценария проверки дашбордов."""

from __future__ import annotations

import os
import logging
import uuid
from typing import Dict, Optional

from aiogram.types import CallbackQuery

from ..bot.formatting.markdown import escape_markdown
from ..bot.keyboards.check import dashboard_check_keyboard
from ..models.dashboards import DashboardCheck
from .bot_access import get_bot
from .config import settings
from .django_client import DjangoAPIClient

logger = logging.getLogger(__name__)

class ChecksRegistry:
    """Registry активных проверок (in-memory)."""

    def __init__(self, django_client: DjangoAPIClient) -> None:
        self._django_client = django_client
        self._active: Dict[str, DashboardCheck] = {}

    def has(self, event_uuid: str) -> bool:
        return event_uuid in self._active

    async def send_dashboard_check(self, check: DashboardCheck) -> bool:
        """Отправляет сообщение о проверке дашборда и регистрирует его как активное."""
        try:
            bot = get_bot()
            keyboard = dashboard_check_keyboard(check.event_uuid)

            message_text = (
                f'<a href="{settings.DJANGO_EXTERNAL_HOST}/admin/check_list/checkevents/{uuid.UUID(check.event_uuid)}/change/">🔧 Событие</a>\n'
                f'👀 Пора проверить дашборд: <b>{check.name}</b>\n\n'
                f'📚 <b>Описание:</b> {check.description}\n\n'
                f'<a href="{check.fake_url}">🔗 Ссылка для проверки</a>\n\n'
                f'⏱ Время на проверку: <b>{check.time_for_check} мин</b>'
            )

            sent = await bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=message_text,
                reply_markup=keyboard,
                parse_mode="HTML",
                disable_web_page_preview=True
            )

            check.message_id = sent.message_id
            self._active[check.event_uuid] = check
            logger.info("Sent dashboard check event=%s name=%s", check.event_uuid, check.name)
            return True
        except Exception as e:
            logger.error("Error sending dashboard check: %s", e, exc_info=True)
            return False

    async def mark_link_clicked(self, event_uuid: str) -> None:
        if event_uuid in self._active:
            self._active[event_uuid].link_clicked = True
            logger.info("Link clicked for event %s", event_uuid)

    async def handle_callback(self, callback: CallbackQuery) -> None:
        """Обработка нажатия inline-кнопок check_ok/check_problem."""
        try:
            if not callback.data:
                await callback.answer("Ошибка в данных кнопки", show_alert=True)
                return

            data_parts = callback.data.split("_")
            if len(data_parts) != 3:
                await callback.answer("Ошибка в данных кнопки", show_alert=True)
                return

            action = data_parts[1]  # ok | problem
            event_uuid = data_parts[2]  # уже строка (uuid.uuid4().hex)

            if event_uuid not in self._active:
                await callback.answer("Эта проверка уже завершена или не найдена", show_alert=True)
                return

            check = self._active[event_uuid]

            if check.is_expired():
                await callback.answer("Время на проверку истекло", show_alert=True)
                await self._finalize_expired(check)
                return

            problem = action == "problem"
            check.button_clicked = True
            check.problem = problem

            success = await self._django_client.send_check_result(event_uuid=event_uuid, problem=problem)
            if not success:
                await callback.answer("Ошибка при отправке результата. Попробуйте еще раз.", show_alert=True)
                return

            status_text = "❌ Есть проблема\\!" if problem else "✅ Все ОК\\!"
            await callback.answer(f"Результат отправлен: {status_text}")
            await self._update_check_message(check)
            self._active.pop(event_uuid, None)

        except Exception as e:
            logger.error("Error handling callback: %s", e, exc_info=True)
            await callback.answer("Произошла ошибка", show_alert=True)

    async def check_expired(self) -> None:
        """Проверяет и завершает истекшие проверки (если кнопка не нажата)."""
        expired = [
            c for c in self._active.values()
            if c.is_expired() and not c.button_clicked
        ]
        for check in expired:
            logger.warning("Check expired event=%s name=%s", check.event_uuid, check.name)
            await self._finalize_expired(check)

    async def _finalize_expired(self, check: DashboardCheck) -> None:
        """Финализация по таймауту"""
        check.problem = False  # считаем, что проблем нет, если не нажали кнопку
        await self._django_client.send_check_result(event_uuid=check.event_uuid, problem=False)
        
        check.problem = None  # для отображения статуса "Время истекло"
        await self._update_check_message(check)
        self._active.pop(check.event_uuid, None)

    async def _update_check_message(self, check: DashboardCheck) -> None:
        if not check.message_id:
            return

        if check.problem is None:
            status_emoji = "⏱"
            status_text = "Время истекло..."
            result_text = f"{status_emoji} Проверка завершена по таймауту"
        elif check.problem:
            status_emoji = "❌"
            status_text = "Есть проблема!"
            result_text = f"{status_emoji} Проверка завершена с проблемами"
        else:
            status_emoji = "✅"
            status_text = "Все ОК!"
            result_text = f"{status_emoji} Проверка завершена успешно"

        updated_text = (
            f'<span class="tg-spoiler">⚓️{uuid.UUID(check.event_uuid)}</span>\n'
            f'<a href="{settings.DJANGO_EXTERNAL_HOST}/admin/check_list/checkevents/{uuid.UUID(check.event_uuid)}/change/">🔧 Событие</a>\n'
            f'🔍 Проверка дашборда: <b>{check.name}</b>\n\n'
            f'{status_emoji} <b>Результат:</b> {status_text}\n'
            f'{result_text}'
        )

        try:
            bot = get_bot()
            await bot.edit_message_text(
                chat_id=settings.TELEGRAM_CHAT_ID,
                message_id=check.message_id,
                text=updated_text,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.warning("Could not update message %s: %s", check.message_id, e)


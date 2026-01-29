"""Фоновые задачи приложения."""

from __future__ import annotations

import asyncio
import logging

from .checks_registry import ChecksRegistry

logger = logging.getLogger(__name__)


async def expired_checks_loop(registry: ChecksRegistry, interval_s: int = 60) -> None:
    """Периодически проверяет истекшие проверки."""
    while True:
        try:
            await asyncio.sleep(interval_s)
            await registry.check_expired()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Error in expired checks loop: %s", e, exc_info=True)


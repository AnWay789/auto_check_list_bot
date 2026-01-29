"""Точка входа приложения: FastAPI + Aiogram (polling) в одном процессе."""

from __future__ import annotations

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Загружаем .env перед импортом settings (на случай запуска вне Poetry)
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()
except Exception:
    pass

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.api import setup_routes
from src.bot.handlers import register_command_handlers, register_callback_handlers
from src.services.bot_access import set_bot
from src.services.checks_registry import ChecksRegistry
from src.services.config import settings
from src.services.django_client import DjangoAPIClient
from src.services.scheduler import expired_checks_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

bot: Bot | None = None
dp: Dispatcher | None = None
django_client: DjangoAPIClient | None = None
bot_task: asyncio.Task | None = None
scheduler_task: asyncio.Task | None = None


async def start_bot(app: FastAPI) -> None:
    """Инициализация и запуск aiogram polling."""
    global bot, dp, django_client

    settings.validate_required()

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    set_bot(bot)
    dp = Dispatcher(storage=MemoryStorage())

    django_client = DjangoAPIClient(base_url=settings.DJANGO_API_URL)
    registry = ChecksRegistry(django_client=django_client)

    # Делаем registry доступным из FastAPI роутов
    app.state.registry = registry

    # Handlers
    register_command_handlers(dp)
    register_callback_handlers(dp, registry)

    logger.info("Starting telegram bot polling...")
    await dp.start_polling(bot, skip_updates=True)


async def stop_bot() -> None:
    """Graceful shutdown бота и клиентов."""
    global bot, dp, django_client

    if dp:
        try:
            await dp.stop_polling()
        except Exception:
            pass

    if bot:
        await bot.session.close()

    if django_client:
        await django_client.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot_task, scheduler_task

    logger.info("Starting application...")

    # Запускаем бота в фоне
    bot_task = asyncio.create_task(start_bot(app))

    # Даем время на создание registry в app.state (start_bot)
    await asyncio.sleep(1)

    # Запускаем scheduler (если registry уже инициализирован)
    try:
        registry: ChecksRegistry = app.state.registry
        scheduler_task = asyncio.create_task(expired_checks_loop(registry))
    except Exception:
        scheduler_task = None

    yield

    logger.info("Shutting down application...")

    if scheduler_task and not scheduler_task.done():
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass

    if bot_task and not bot_task.done():
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass

    await stop_bot()


app = FastAPI(
    title="Auto Check List Bot API",
    description="FastAPI + Telegram bot for dashboard checklist",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_routes(app)


def main() -> None:
    logger.info("Starting API server on %s:%s", settings.API_HOST, settings.API_PORT)
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT, log_level="info")


if __name__ == "__main__":
    main()


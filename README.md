# Auto Check List Bot

Телеграм бот для автоматизированной проверки дашбордов.

## Описание

Бот получает список дашбордов для проверки от Django приложения через FastAPI, отправляет уведомления в Telegram с кнопками для подтверждения проверки, отслеживает переходы по ссылкам и отправляет результаты обратно в Django.

## Быстрый старт

```bash
git clone <url> && cd auto_check_list_bot
poetry install
cp .env.example .env
# отредактируйте .env и укажите TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID
poetry run python main.py
```

Файл `.env` не попадает в репозиторий (см. `.gitignore`); для работы нужен свой `.env` на основе `.env.example`.

## Переменные окружения

- `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота (получить у @BotFather)
- `TELEGRAM_CHAT_ID` - ID чата куда отправлять сообщения
- `DJANGO_API_URL` - URL Django приложения (по умолчанию http://localhost:8000)
- `DJANGO_CALLBACK_ENDPOINT` - endpoint Django для приема результатов (по умолчанию `/api/dashbord_colback/`)

## Запуск

```bash
poetry run python main.py
```

Совместимость со старым способом запуска (thin-wrapper):

```bash
poetry run python -m auto_check_list_bot
```

## Получение TELEGRAM_CHAT_ID

Чтобы узнать ID чата, куда отправлять сообщения:

1. Создайте бота через @BotFather в Telegram
2. Добавьте бота в нужный чат или начните диалог с ботом
3. Отправьте боту любое сообщение
4. Откройте в браузере: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
5. Найдите `"chat":{"id":123456789}` - это и есть ваш CHAT_ID

## API Endpoints

### POST /api/send_message/
Принимает список дашбордов для проверки от Django приложения.

**Request:**
```json
{
  "dashboards": [
    {
      "event_uuid": "uuid",
      "dashboard_uid": "string",
      "name": "string",
      "real_url": "string",
      "fake_url": "string",
      "time_for_check": 30
    }
  ]
}
```

### GET /api/link_clicked/{event_uuid}
Отслеживает переходы по ссылке (вызывается при переходе по fake_url).

### GET /health
Health check endpoint.

## Структура проекта

```
main.py
src/
├── api/                 # FastAPI роутеры
├── bot/                 # aiogram handlers / keyboards / formatting
├── models/              # Pydantic модели
└── services/            # config / django client / registry / scheduler
```

## Как это работает

1. Django приложение через Celery задачу отправляет список дашбордов на `/api/send_message/`
2. Бот получает дашборды и отправляет сообщения в Telegram с кнопками
3. Пользователь переходит по fake_url (которая редиректит на real_url через Django)
4. Django отслеживает переход и может уведомить бота (опционально)
5. Пользователь нажимает кнопку "Все ОК!" или "Есть проблема!"
6. Бот отправляет результат обратно в Django через `/api/dashbord_colback/`
7. Если время истекло, бот автоматически помечает проверку как проблемную

## Интеграция с Django

Бот ожидает, что Django приложение:
- Отправляет дашборды на `http://localhost:8001/api/send_message/`
- Имеет эндпоинт `/api/dashbord_colback/` для приема результатов проверки
- Имеет эндпоинт `/to_dashboard/{event_uuid}/` для редиректа на реальный дашборд

## Документация

Полная документация в папке `docs/`:

- `docs/README.md` — обзор и структура
- `docs/FLOWS.md` — потоки
- `docs/API.md` — API
- `docs/SETUP.md` — установка и запуск

## Репозиторий

- `.gitignore` — исключает из коммита `.env`, кэши Python, виртуальные окружения, артефакты сборки и тестов, служебные файлы IDE и ОС.

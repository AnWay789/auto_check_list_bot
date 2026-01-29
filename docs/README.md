## Auto Check List Bot — документация

Проект: Telegram-бот для автоматизированной проверки дашбордов. Django присылает список дашбордов на FastAPI, бот отправляет сообщение в Telegram с кнопками, результат уходит обратно в Django.

### Структура проекта

```
auto_check_list_bot/
├── main.py                     # Точка входа (FastAPI + aiogram polling + scheduler)
├── src/
│   ├── api/                    # FastAPI роуты
│   │   ├── health.py           # /health
│   │   └── checks.py           # /api/send_message/, /api/link_clicked, /api/checks/send
│   ├── bot/
│   │   ├── handlers/           # обработчики команд и callback-кнопок
│   │   ├── keyboards/          # клавиатуры (inline buttons)
│   │   └── formatting/         # утилиты форматирования
│   ├── models/                 # Pydantic модели
│   └── services/               # конфиг, Django client, registry, scheduler
└── src/auto_check_list_bot/     # минимальная совместимость для `python -m auto_check_list_bot`
```

### Важные файлы в корне

- `main.py` — точка входа приложения
- `pyproject.toml` / `poetry.lock` — зависимости (Poetry)
- `.env.example` — шаблон переменных окружения (копировать в `.env`)
- `.gitignore` — исключения для Git (в т.ч. `.env`, кэши, venv, артефакты тестов)
- `Dockerfile` — образ для запуска в Docker

### Навигация

- `docs/FLOWS.md` — потоки и “как это работает”
- `docs/API.md` — описание HTTP API
- `docs/SETUP.md` — установка и запуск


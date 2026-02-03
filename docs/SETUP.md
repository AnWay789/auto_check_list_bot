## Установка и запуск

### Требования

- Python 3.13+
- Poetry

### Клонирование и установка

```bash
git clone <url-репозитория> && cd auto_check_list_bot
poetry install
```

Переменные окружения задаются в **общем `.env` в родительской директории** (каталог, содержащий оба проекта: `auto_check_list` и `auto_check_list_bot`). Создайте там файл `.env` из `.env.example` (из любого из проектов) и заполните переменные. Файл `.env` в репозиторий не входит (указан в `.gitignore`).

### Переменные окружения

Смотрите `.env.example`. Обязательные:

- `TELEGRAM_BOT_TOKEN` — токен бота
- `TELEGRAM_CHAT_ID` — чат, куда слать уведомления (может быть `-100...`)
- `DJANGO_API_URL` — базовый URL Django приложения (например `http://localhost:8000`)
- `DJANGO_CALLBACK_ENDPOINT` — endpoint для callback (например `/api/dashbord_colback/`)

Опциональные:

- `API_HOST` (по умолчанию `0.0.0.0`)
- `API_PORT` (по умолчанию `8001`)

### Запуск

Основной способ:

```bash
poetry run python main.py
```

Совместимость со старым способом (оставлен thin-wrapper):

```bash
poetry run python -m auto_check_list_bot
```

### Запуск через Docker Compose родительского проекта

Бот можно запускать как сервис `telegram_bot` из Docker Compose проекта Django (`auto_check_list`):

- В **родительской директории обоих проектов** (каталог, содержащий `auto_check_list` и `auto_check_list_bot`) создайте общий `.env` на основе `.env.example` и заполните:
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID`
  - при необходимости `TELEGRAM_PJ_PATH=./auto_check_list_bot`
- По умолчанию Django обращается к боту по `TELEGRAM_URL=telegram_bot:8001`, а бот к Django по `DJANGO_API_URL=http://web:8000`.

После этого достаточно выполнить в каталоге `auto_check_list` (при настроенном в `docker-compose.yml` чтении `env_file: ../.env`):

```bash
docker-compose up -d --build
```

Сервис бота будет доступен по адресу `http://localhost:8001` (FastAPI API) и будет автоматически взаимодействовать с Django.


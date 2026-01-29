## Потоки и как это работает

### Общая схема

```mermaid
sequenceDiagram
participant Django
participant FastAPI
participant Registry
participant Telegram

Django->>FastAPI: POST /api/send_message/
FastAPI->>Registry: create DashboardCheck + send
Registry->>Telegram: send_message(chat_id=TELEGRAM_CHAT_ID, buttons)

Telegram-->>Registry: callback check_ok|check_problem
Registry->>Django: POST DJANGO_CALLBACK_ENDPOINT
Registry->>Telegram: edit_message_text(status)

loop every60s
Registry->>Registry: check_expired()
Registry->>Django: POST DJANGO_CALLBACK_ENDPOINT (expired=problem=True)
Registry->>Telegram: edit_message_text(expired)
end
```

### Что где находится

- `main.py`: поднимает FastAPI и запускает aiogram polling в фоне (lifespan), а также периодическую задачу таймаутов.
- `src/services/checks_registry.py`: **бизнес-логика** сценария проверки:
  - отправка сообщения в Telegram, хранение активных проверок
  - обработка callback-кнопок
  - завершение по таймауту и обновление сообщения
- `src/api/checks.py`: HTTP входные точки от Django (`/api/send_message/`, `/api/link_clicked/{event_uuid}`) + новый более строгий endpoint (`/api/checks/send`).
- `src/services/django_client.py`: отправка результата проверки обратно в Django.


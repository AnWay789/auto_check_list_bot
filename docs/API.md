## HTTP API

### Health

- `GET /health`
  - **Response**: `{"status":"healthy"}`

### Приём списка дашбордов от Django (legacy, сохранён)

- `POST /api/send_message/`
  - **Назначение**: принять список дашбордов и отправить уведомления в Telegram.
  - **Request**:

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

  - **Response** (как раньше — поэлементно):

```json
{
  "status": "ok",
  "processed": 1,
  "results": [
    { "event_uuid": "uuid", "success": true }
  ]
}
```

### Приём списка дашбордов (новый, строгий)

- `POST /api/checks/send`
  - **Назначение**: то же самое, но запрос валидируется строго целиком (Pydantic модель).
  - **Request/Response**: по формату совпадает с legacy, но при невалидном payload вернёт `400` сразу.

### Отметить переход по ссылке (legacy, сохранён)

- `GET /api/link_clicked/{event_uuid}`
  - **Назначение**: отметить, что пользователь перешёл по ссылке (fake_url).
  - **Response**: `{"status":"ok","event_uuid":"..."}`.

### Что изменилось по сравнению со старой реализацией

- Старые пути **сохранены**: `/api/send_message/`, `/api/link_clicked/{event_uuid}`, `/health`.
- Добавлен новый структурированный endpoint: `POST /api/checks/send`.
- Внутренняя архитектура переписана: кнопки/handlers/api/services разнесены по модулям (см. `docs/README.md` и `docs/FLOWS.md`).


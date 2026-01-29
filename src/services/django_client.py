"""HTTP клиент для взаимодействия с Django API."""

from __future__ import annotations

import logging

import httpx

from .config import settings

logger = logging.getLogger(__name__)


class DjangoAPIClient:
    """Клиент для взаимодействия с Django API."""

    def __init__(self, base_url: str | None = None, timeout_s: float = 30.0) -> None:
        self.base_url = (base_url or settings.DJANGO_API_URL).rstrip("/")
        self.callback_endpoint = settings.DJANGO_CALLBACK_ENDPOINT
        self._client = httpx.AsyncClient(timeout=timeout_s)

    async def close(self) -> None:
        await self._client.aclose()

    async def send_check_result(self, event_uuid: str, problem: bool) -> bool:
        url = f"{self.base_url}{self.callback_endpoint}"
        payload = {"event_uuid": event_uuid, 
                   "problem": problem}
        try:
            resp = await self._client.post(url, json=payload)
            resp.raise_for_status()
            logger.info("Sent check result event=%s problem=%s", event_uuid, problem)
            return True
        except httpx.TimeoutException:
            logger.error("Timeout while sending check result to %s", url)
            return False
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error %s while sending check result: %s",
                e.response.status_code,
                e.response.text,
            )
            return False
        except Exception as e:
            logger.error("Unexpected error while sending check result: %s", e, exc_info=True)
            return False


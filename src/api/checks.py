"""API endpoints для приема задач проверки дашбордов."""

from __future__ import annotations

import logging
from typing import Any, List

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..models.dashboards import DashboardInfo, DashboardCheck

logger = logging.getLogger(__name__)

router = APIRouter()


class SendMessagePayload(BaseModel):
    dashboards: List[DashboardInfo]

# @router.post("/api/checks/send")
# async def send_checks(payload: SendMessagePayload, request: Request) -> dict[str, Any]:
#     """Новый (структурированный) endpoint отправки проверок."""
#     registry = request.app.state.registry
#     results: list[dict[str, Any]] = []

#     for info in payload.dashboards:
#         check = DashboardCheck.from_dashboard_info(info)
#         success = await registry.send_dashboard_check(check)
#         results.append({"event_uuid": info.event_uuid, "success": success})

#     return {"status": "ok", "processed": len(results), "results": results}


@router.post("/api/checks/send")
async def send_message_legacy(payload: dict, request: Request) -> dict[str, Any]:
    if "dashboards" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'dashboards' field in payload")
    dashboards_data = payload["dashboards"]
    if not isinstance(dashboards_data, list):
        raise HTTPException(status_code=400, detail="'dashboards' must be a list")

    registry = request.app.state.registry
    results: list[dict[str, Any]] = []

    for dashboard_dict in dashboards_data:
        try:
            info = DashboardInfo.model_validate(dashboard_dict)
            check = DashboardCheck.from_dashboard_info(info)
            success = await registry.send_dashboard_check(check)
            results.append({"event_uuid": info.event_uuid, "success": success})
        except Exception as e:
            logger.error("Error processing dashboard: %s", e, exc_info=True)
            results.append(
                {
                    "event_uuid": dashboard_dict.get("event_uuid", "unknown"),
                    "success": False,
                    "error": str(e),
                }
            )

    return {"status": "ok", "processed": len(results), "results": results}


# @router.get("/api/link_clicked/{event_uuid}")
# async def link_clicked(event_uuid: str, request: Request) -> dict[str, str]:
#     """Legacy endpoint: отметить переход по ссылке."""
#     try:
#         registry = request.app.state.registry
#         await registry.mark_link_clicked(event_uuid)
#         return {"status": "ok", "event_uuid": event_uuid}
#     except Exception as e:
#         logger.error("Error marking link clicked: %s", e, exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))


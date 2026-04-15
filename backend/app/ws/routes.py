"""WebSocket маршруты для чата и трекинга экстренных заявок."""

import uuid

import structlog
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import get_current_user_ws
from app.models.user import User
from app.services.chat import get_messages, mark_room_read, send_message
from app.services.emergency import get_emergency
from app.schemas.chat import SendMessageRequest
from app.models.chat import MessageType
from app.ws.manager import manager

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/chat/{room_id}")
async def ws_chat(
    ws: WebSocket,
    room_id: uuid.UUID,
    token: str = Query(..., description="JWT access token"),
    db: AsyncSession = Depends(get_session),
) -> None:
    """WebSocket endpoint чата.

    Протокол сообщений (JSON):
    - Клиент → сервер: {"type": "message", "content": "текст", "message_type": "text"}
    - Сервер → клиент: {"type": "message", ...ChatMessageResponse fields...}
    - Сервер → клиент: {"type": "read", "room_id": "..."}
    - Сервер → клиент: {"type": "error", "detail": "..."}
    """
    current_user: User | None = await get_current_user_ws(token, db)
    if not current_user:
        await ws.close(code=4001, reason="Unauthorized")
        return

    room_id_str = str(room_id)
    user_id_str = str(current_user.id)

    await manager.connect(ws, room_id_str, user_id_str)
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")

            if msg_type == "message":
                request = SendMessageRequest(
                    content=data.get("content", ""),
                    message_type=data.get("message_type", MessageType.text),
                    file_url=data.get("file_url"),
                    file_name=data.get("file_name"),
                )
                try:
                    msg = await send_message(room_id, current_user.id, request, db)
                    payload = {"type": "message", **msg.model_dump(mode="json")}
                    await manager.broadcast_to_room(room_id_str, payload)
                except Exception as exc:
                    await ws.send_json({"type": "error", "detail": str(exc)})

            elif msg_type == "read":
                await mark_room_read(room_id, current_user.id, db)
                await manager.broadcast_to_room(
                    room_id_str,
                    {"type": "read", "room_id": room_id_str, "user_id": user_id_str},
                )

    except WebSocketDisconnect:
        manager.disconnect(ws, room_id_str, user_id_str)
    except Exception as exc:
        logger.warning("ws_chat_error", error=str(exc))
        manager.disconnect(ws, room_id_str, user_id_str)


@router.websocket("/ws/emergency/{request_id}")
async def ws_emergency(
    ws: WebSocket,
    request_id: uuid.UUID,
    token: str = Query(..., description="JWT access token"),
    db: AsyncSession = Depends(get_session),
) -> None:
    """WebSocket endpoint трекинга экстренной заявки.

    Сервер шлёт обновления статуса заявки:
    - {"type": "status_update", "status": "partner_found", "partner_id": "..."}
    - {"type": "location_update", "lat": 55.75, "lon": 37.62, "eta_minutes": 12}
    Соединение только читающее — клиент ничего не отправляет.
    """
    current_user: User | None = await get_current_user_ws(token, db)
    if not current_user:
        await ws.close(code=4001, reason="Unauthorized")
        return

    room_id_str = f"emergency:{request_id}"
    user_id_str = str(current_user.id)

    await manager.connect(ws, room_id_str, user_id_str)
    try:
        # Сразу отправляем текущее состояние
        try:
            emergency = await get_emergency(request_id, current_user.id, db)
            await ws.send_json(
                {"type": "snapshot", **emergency.model_dump(mode="json")}
            )
        except Exception as exc:
            await ws.send_json({"type": "error", "detail": str(exc)})
            manager.disconnect(ws, room_id_str, user_id_str)
            return

        # Держим соединение открытым — обновления шлёт сервис
        while True:
            # Ожидаем ping от клиента чтобы держать соединение
            await ws.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(ws, room_id_str, user_id_str)
    except Exception as exc:
        logger.warning("ws_emergency_error", error=str(exc))
        manager.disconnect(ws, room_id_str, user_id_str)

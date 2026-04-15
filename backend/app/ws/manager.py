"""WebSocket Connection Manager для чата и экстренной помощи."""

import json
import uuid
from collections import defaultdict

import structlog
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

logger = structlog.get_logger(__name__)


class ConnectionManager:
    """Управляет активными WebSocket-соединениями.

    Структура хранения:
    - _room_connections: {room_id: {user_id: [WebSocket, ...]}}
    - _user_connections: {user_id: [WebSocket, ...]}  — для личных push-уведомлений
    """

    def __init__(self) -> None:
        self._room_connections: dict[str, dict[str, list[WebSocket]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self._user_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(
        self,
        ws: WebSocket,
        room_id: str,
        user_id: str,
    ) -> None:
        await ws.accept()
        self._room_connections[room_id][user_id].append(ws)
        self._user_connections[user_id].append(ws)
        logger.info("ws_connected", room_id=room_id, user_id=user_id)

    def disconnect(self, ws: WebSocket, room_id: str, user_id: str) -> None:
        room = self._room_connections.get(room_id, {})
        connections = room.get(user_id, [])
        if ws in connections:
            connections.remove(ws)
        if not connections:
            room.pop(user_id, None)
        if not room:
            self._room_connections.pop(room_id, None)

        user_ws = self._user_connections.get(user_id, [])
        if ws in user_ws:
            user_ws.remove(ws)
        if not user_ws:
            self._user_connections.pop(user_id, None)

        logger.info("ws_disconnected", room_id=room_id, user_id=user_id)

    async def broadcast_to_room(self, room_id: str, payload: dict) -> None:
        """Рассылает сообщение всем участникам комнаты."""
        text = json.dumps(payload, ensure_ascii=False, default=str)
        dead: list[tuple[str, WebSocket]] = []

        for uid, sockets in list(self._room_connections.get(room_id, {}).items()):
            for ws in list(sockets):
                try:
                    if ws.client_state == WebSocketState.CONNECTED:
                        await ws.send_text(text)
                    else:
                        dead.append((uid, ws))
                except Exception:
                    dead.append((uid, ws))

        for uid, ws in dead:
            self.disconnect(ws, room_id, uid)

    async def send_to_user(self, user_id: str, payload: dict) -> None:
        """Отправляет персональное сообщение пользователю (все его вкладки)."""
        text = json.dumps(payload, ensure_ascii=False, default=str)
        for ws in list(self._user_connections.get(user_id, [])):
            try:
                if ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_text(text)
            except Exception:
                pass

    def room_user_count(self, room_id: str) -> int:
        return len(self._room_connections.get(room_id, {}))


# Синглтон — все роутеры используют один и тот же экземпляр
manager = ConnectionManager()

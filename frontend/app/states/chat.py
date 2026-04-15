"""Chat State — Phase 2: чат между клиентом и партнёром."""

import httpx
import reflex as rx

from app.api import API_V1
from app.state import AppState


class ChatState(AppState):
    rooms: list[dict] = []
    rooms_loading: bool = False

    active_room_id: str = ""
    active_room: dict = {}
    messages: list[dict] = []
    messages_loading: bool = False

    new_message: str = ""
    send_loading: bool = False

    async def load_rooms(self):
        if not self.access_token:
            return
        self.rooms_loading = True
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/chat/rooms",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    self.rooms = resp.json()
            except Exception:
                pass
        self.rooms_loading = False

    async def open_room(self, room_id: str):
        self.active_room_id = room_id
        self.messages = []
        # Find room info
        for r in self.rooms:
            if str(r.get("id")) == room_id:
                self.active_room = r
                break
        yield ChatState.load_messages()
        yield ChatState.mark_read()

    async def load_messages(self):
        if not self.active_room_id or not self.access_token:
            return
        self.messages_loading = True
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/chat/rooms/{self.active_room_id}/messages",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params={"limit": 50},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    self.messages = resp.json()
            except Exception:
                pass
        self.messages_loading = False

    async def send_message(self):
        content = self.new_message.strip()
        if not content or not self.active_room_id:
            return
        self.send_loading = True
        self.new_message = ""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{API_V1}/chat/rooms/{self.active_room_id}/messages",
                    json={"content": content, "message_type": "text"},
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 201:
                    self.messages = [*self.messages, resp.json()]
            except Exception:
                pass
        self.send_loading = False

    async def mark_read(self):
        if not self.active_room_id or not self.access_token:
            return
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"{API_V1}/chat/rooms/{self.active_room_id}/read",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
            except Exception:
                pass

    async def open_or_create_room(self, order_id: str, partner_user_id: str):
        if not self.access_token:
            yield rx.redirect("/login")
            return
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{API_V1}/chat/rooms",
                    json={
                        "room_type": "order",
                        "order_id": order_id,
                        "partner_user_id": partner_user_id,
                    },
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code in (200, 201):
                    data = resp.json()
                    yield ChatState.load_rooms()
                    yield ChatState.open_room(str(data.get("id", "")))
                    yield rx.redirect("/chat")
            except Exception:
                pass

    async def poll_messages(self):
        """Поллинг новых сообщений (вызывается через set_interval)."""
        if not self.active_room_id or not self.access_token:
            return
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/chat/rooms/{self.active_room_id}/messages",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params={"limit": 50},
                    timeout=8.0,
                )
                if resp.status_code == 200:
                    new_msgs = resp.json()
                    if len(new_msgs) != len(self.messages):
                        self.messages = new_msgs
            except Exception:
                pass


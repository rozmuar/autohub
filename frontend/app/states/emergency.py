"""Emergency State — Phase 2: экстренная помощь."""

import httpx
import reflex as rx

from app.api import API_V1
from app.state import AppState

EMERGENCY_TYPES = [
    ("tow_truck", "🚛 Эвакуатор"),
    ("jump_start", "🔋 Прикурить"),
    ("fuel", "⛽ Топливо"),
    ("tire", "🔧 Шиномонтаж"),
    ("stuck", "❄️ Застрял"),
    ("other", "🆘 Другое"),
]


class EmergencyState(AppState):
    # Step: type → confirm → searching → found → inprogress
    em_step: str = "type"
    em_type: str = ""
    em_description: str = ""
    em_address: str = ""
    em_lat: float = 0.0
    em_lon: float = 0.0

    em_request_id: str = ""
    em_request: dict = {}
    em_responses: list[dict] = []
    em_status: str = ""
    em_eta: int = 0

    em_loading: bool = False
    em_error: str = ""

    async def create_request(self):
        if not self.em_type:
            self.em_error = "Выберите тип помощи"
            return
        if not self.access_token:
            return rx.redirect("/login")
        self.em_loading = True
        self.em_error = ""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{API_V1}/emergency",
                    json={
                        "emergency_type": self.em_type,
                        "latitude": self.em_lat or 55.7558,
                        "longitude": self.em_lon or 37.6173,
                        "address": self.em_address or "Местоположение не определено",
                        "description": self.em_description or None,
                    },
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=15.0,
                )
                if resp.status_code == 201:
                    data = resp.json()
                    self.em_request_id = str(data.get("id", ""))
                    self.em_request = data
                    self.em_status = data.get("status", "searching")
                    self.em_step = "searching"
                else:
                    self.em_error = resp.json().get("detail", "Ошибка создания заявки")
            except Exception:
                self.em_error = "Ошибка соединения с сервером"
        self.em_loading = False

    async def poll_status(self):
        """Опрос статуса заявки каждые 3 сек."""
        if not self.em_request_id or not self.access_token:
            return
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/emergency/{self.em_request_id}",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.em_request = data
                    self.em_status = data.get("status", self.em_status)
                    self.em_responses = data.get("responses", [])
                    self.em_eta = data.get("estimated_arrival_minutes", 0) or 0
                    if self.em_status == "partner_found":
                        self.em_step = "found"
                    elif self.em_status == "in_progress":
                        self.em_step = "inprogress"
                    elif self.em_status == "completed":
                        self.em_step = "done"
            except Exception:
                pass

    async def cancel_request(self):
        if not self.em_request_id:
            return
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"{API_V1}/emergency/{self.em_request_id}/cancel",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
            except Exception:
                pass
        self.em_step = "type"
        self.em_request_id = ""
        self.em_request = {}
        self.em_responses = []
        self.em_error = ""

    def select_type(self, t: str):
        self.em_type = t
        self.em_error = ""

    def em_reset(self):
        self.em_step = "type"
        self.em_type = ""
        self.em_description = ""
        self.em_address = ""
        self.em_request_id = ""
        self.em_request = {}
        self.em_responses = []
        self.em_status = ""
        self.em_error = ""

    def go_confirm(self):
        if not self.em_type:
            self.em_error = "Выберите тип помощи"
            return
        self.em_step = "confirm"

    def back_to_type(self):
        self.em_step = "type"
        self.em_error = ""

    @rx.var
    def em_type_label(self) -> str:
        for t, label in EMERGENCY_TYPES:
            if t == self.em_type:
                return label
        return ""


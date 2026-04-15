"""Booking State — slot calendar and booking creation."""

import httpx
import reflex as rx

from app.api import API_V1
from app.state import AppState


class BookingState(AppState):
    booking_partner_id: str = ""
    service_id: str = ""
    vehicle_id: str = ""

    available_slots: list[dict] = []
    slots_loading: bool = False
    selected_slot_id: str = ""

    booking_loading: bool = False
    booking_error: str = ""
    booking_success: bool = False
    created_booking_id: str = ""

    # Date range (YYYY-MM-DD)
    date_from: str = ""
    date_to: str = ""

    user_vehicles: list[dict] = []

    async def load_slots(self):
        if not self.booking_partner_id:
            return
        self.slots_loading = True
        params: dict = {"partner_id": self.booking_partner_id}
        if self.service_id:
            params["service_id"] = self.service_id
        if self.date_from:
            params["date_from"] = self.date_from
        if self.date_to:
            params["date_to"] = self.date_to
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/bookings/slots",
                    params=params,
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.available_slots = data.get("items", data) if isinstance(data, dict) else data
            except Exception:
                pass
        self.slots_loading = False

    async def load_user_vehicles(self):
        if not self.access_token:
            return
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/vehicles",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.user_vehicles = data.get("items", data) if isinstance(data, dict) else data
            except Exception:
                pass

    async def create_booking(self):
        if not self.selected_slot_id:
            self.booking_error = "Выберите время"
            return
        if not self.access_token:
            return rx.redirect("/login")
        self.booking_loading = True
        self.booking_error = ""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{API_V1}/bookings",
                    json={
                        "slot_id": self.selected_slot_id,
                        "vehicle_id": self.vehicle_id or None,
                        "service_id": self.service_id or None,
                    },
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=15.0,
                )
                if resp.status_code == 201:
                    data = resp.json()
                    self.created_booking_id = str(data.get("id", ""))
                    self.booking_success = True
                else:
                    self.booking_error = resp.json().get("detail", "Ошибка бронирования")
            except Exception:
                self.booking_error = "Ошибка соединения"
        self.booking_loading = False

    def select_slot(self, slot_id: str):
        self.selected_slot_id = slot_id
        self.booking_error = ""

    def init_booking(self, partner_id: str, service_id: str = ""):
        self.booking_partner_id = partner_id
        self.service_id = service_id
        self.selected_slot_id = ""
        self.booking_success = False
        self.booking_error = ""
        self.available_slots = []


"""Partner State — registration wizard and profile management."""

import httpx
import reflex as rx

from app.api import API_V1
from app.state import AppState


class PartnerState(AppState):
    # Registration wizard: step 1=info, 2=address, 3=confirm
    reg_step: int = 1
    reg_company_name: str = ""
    reg_partner_type: str = "individual"
    reg_inn: str = ""
    reg_description: str = ""
    reg_phone: str = ""
    reg_address: str = ""
    reg_city: str = ""
    reg_loading: bool = False
    reg_error: str = ""

    # Partner profile
    partner_profile: dict = {}
    partner_loading: bool = False

    # Services
    services: list[dict] = []
    services_loading: bool = False
    svc_dialog_open: bool = False
    svc_name: str = ""
    svc_price: str = ""
    svc_duration: int = 60
    svc_description: str = ""
    svc_loading: bool = False
    svc_error: str = ""

    # Schedule
    schedule: list[dict] = []
    schedule_loading: bool = False

    # Analytics
    analytics_date_from: str = ""
    analytics_date_to: str = ""
    analytics_data: dict = {}
    analytics_loading: bool = False
    top_services: list[dict] = []

    def reg_next(self):
        if self.reg_step == 1:
            if not self.reg_company_name or not self.reg_inn:
                self.reg_error = "Заполните все обязательные поля"
                return
            self.reg_error = ""
            self.reg_step = 2
        elif self.reg_step == 2:
            if not self.reg_address:
                self.reg_error = "Введите адрес"
                return
            self.reg_error = ""
            self.reg_step = 3

    def reg_back(self):
        if self.reg_step > 1:
            self.reg_step -= 1
            self.reg_error = ""

    def set_svc_duration(self, v: str):
        try:
            self.svc_duration = int(v)
        except (ValueError, TypeError):
            self.svc_duration = 60

    async def submit_registration(self):
        self.reg_loading = True
        self.reg_error = ""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{API_V1}/partners",
                    json={
                        "company_name": self.reg_company_name,
                        "partner_type": self.reg_partner_type,
                        "inn": self.reg_inn,
                        "description": self.reg_description or None,
                        "phone": self.reg_phone or None,
                        "address": self.reg_address,
                        "city": self.reg_city or None,
                    },
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=15.0,
                )
                if resp.status_code in (200, 201):
                    yield PartnerState.load_partner_profile()
                    yield rx.redirect("/partner/dashboard")
                else:
                    self.reg_error = resp.json().get("detail", "Ошибка регистрации")
            except Exception:
                self.reg_error = "Ошибка соединения"
        self.reg_loading = False

    async def load_partner_profile(self):
        if not self.access_token:
            return
        self.partner_loading = True
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/partners/me",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    self.partner_profile = resp.json()
                elif resp.status_code == 404:
                    yield rx.redirect("/partner/register")
            except Exception:
                pass
        self.partner_loading = False

    async def load_services(self):
        if not self.access_token:
            return
        self.services_loading = True
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/catalog/my-services",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.services = data.get("items", data) if isinstance(data, dict) else data
            except Exception:
                pass
        self.services_loading = False

    async def add_service(self):
        if not self.svc_name:
            self.svc_error = "Введите название услуги"
            return
        self.svc_loading = True
        self.svc_error = ""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{API_V1}/catalog/services",
                    json={
                        "name": self.svc_name,
                        "price": float(self.svc_price) if self.svc_price else 0.0,
                        "duration_minutes": self.svc_duration,
                        "description": self.svc_description or None,
                    },
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 201:
                    self.services = [*self.services, resp.json()]
                    self.svc_dialog_open = False
                    self.svc_name = ""
                    self.svc_price = ""
                    self.svc_description = ""
                else:
                    self.svc_error = resp.json().get("detail", "Ошибка добавления")
            except Exception:
                self.svc_error = "Ошибка соединения"
        self.svc_loading = False

    async def delete_service(self, service_id: str):
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.delete(
                    f"{API_V1}/catalog/services/{service_id}",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 204:
                    self.services = [s for s in self.services if str(s.get("id")) != service_id]
            except Exception:
                pass

    async def load_analytics(self):
        if not self.access_token or not self.analytics_date_from or not self.partner_profile:
            return
        self.analytics_loading = True
        partner_id = str(self.partner_profile.get("id", ""))
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/analytics/partner/{partner_id}/dashboard",
                    params={"date_from": self.analytics_date_from, "date_to": self.analytics_date_to},
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=15.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.analytics_data = data
                    self.top_services = data.get("top_services", [])
            except Exception:
                pass
        self.analytics_loading = False

    async def load_schedule(self):
        if not self.access_token:
            return
        self.schedule_loading = True
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/partners/me/schedule",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    self.schedule = resp.json()
                elif resp.status_code == 404:
                    # Инициализировать дефолтным расписанием
                    days = [
                        ("monday", "Понедельник"), ("tuesday", "Вторник"),
                        ("wednesday", "Среда"), ("thursday", "Четверг"),
                        ("friday", "Пятница"), ("saturday", "Суббота"),
                        ("sunday", "Воскресенье"),
                    ]
                    self.schedule = [
                        {
                            "day_of_week": d,
                            "day_label": label,
                            "is_working": d not in ("saturday", "sunday"),
                            "open_time": "09:00",
                            "close_time": "18:00",
                        }
                        for d, label in days
                    ]
            except Exception:
                pass
        self.schedule_loading = False

    async def save_schedule(self):
        if not self.access_token or not self.schedule:
            return
        async with httpx.AsyncClient() as client:
            try:
                await client.put(
                    f"{API_V1}/partners/me/schedule",
                    json=self.schedule,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
            except Exception:
                pass

    def toggle_day(self, day_of_week: str):
        self.schedule = [
            {**d, "is_working": not d["is_working"]} if d["day_of_week"] == day_of_week else d
            for d in self.schedule
        ]


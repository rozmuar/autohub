"""Глобальный State приложения."""

import httpx
import reflex as rx

from app.api import API_V1


class AppState(rx.State):
    """Базовый State — аутентификация и профиль текущего пользователя."""

    access_token: str = rx.LocalStorage("")
    refresh_token: str = rx.LocalStorage("")
    is_authenticated: bool = False
    user_role: str = ""  # client | partner | admin

    user_id: str = ""
    user_name: str = ""
    user_phone: str = ""
    user_email: str = ""
    user_avatar: str = ""

    def sign_out(self):
        self.access_token = ""
        self.refresh_token = ""
        self.is_authenticated = False
        self.user_role = ""
        self.user_id = ""
        self.user_name = ""
        self.user_phone = ""
        self.user_email = ""
        return rx.redirect("/login")

    async def load_profile(self):
        if not self.access_token:
            return
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/users/me",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.user_id = str(data.get("id", ""))
                    first = (data.get("first_name") or "").strip()
                    last = (data.get("last_name") or "").strip()
                    self.user_name = (first + " " + last).strip()
                    self.user_phone = data.get("phone", "") or ""
                    self.user_email = data.get("email", "") or ""
                    self.user_avatar = data.get("avatar_url", "") or ""
                    self.user_role = data.get("role", "client")
                    self.is_authenticated = True
                elif resp.status_code == 401:
                    yield AppState.sign_out()
            except Exception:
                pass

    @rx.var
    def is_partner(self) -> bool:
        return self.user_role == "partner"

    @rx.var
    def is_client(self) -> bool:
        return self.user_role in ("client", "")

    @rx.var
    def is_admin(self) -> bool:
        return self.user_role == "admin"

    @rx.var
    def display_name(self) -> str:
        return self.user_name or self.user_phone or "Пользователь"


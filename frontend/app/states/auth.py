"""Auth State — OTP-based login and registration."""

import httpx
import reflex as rx

from app.api import API_V1
from app.state import AppState


class AuthState(AppState):
    """OTP-авторизация и регистрация."""

    auth_step: str = "phone"  # phone | otp | register
    auth_phone: str = ""
    auth_otp: str = "0000"
    auth_name: str = ""
    auth_email: str = ""
    auth_error: str = ""
    auth_loading: bool = False

    async def send_otp(self):
        if not self.auth_phone:
            self.auth_error = "Введите номер телефона"
            return
        self.auth_loading = True
        self.auth_error = ""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{API_V1}/auth/otp/send",
                    json={"phone": self.auth_phone, "purpose": "login"},
                    timeout=15.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    dev_code = data.get("dev_code")
                    if dev_code:
                        # Dev mode: bypass OTP screen entirely
                        self.auth_otp = str(dev_code)
                        yield AuthState.verify_otp()
                    else:
                        self.auth_step = "otp"
                else:
                    self.auth_error = resp.json().get("detail", "Ошибка отправки кода")
            except Exception:
                self.auth_error = "Ошибка соединения с сервером"
        self.auth_loading = False

    async def verify_otp(self):
        if not self.auth_otp:
            self.auth_error = "Введите код"
            return
        self.auth_loading = True
        self.auth_error = ""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{API_V1}/auth/otp/verify",
                    json={"phone": self.auth_phone, "code": self.auth_otp},
                    timeout=15.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("is_registered", False):
                        self.access_token = data.get("access_token", "")
                        self.refresh_token = data.get("refresh_token", "")
                        yield AppState.load_profile()
                        yield rx.redirect("/")
                    else:
                        self.auth_step = "register"
                else:
                    self.auth_error = resp.json().get("detail", "Неверный код")
            except Exception:
                self.auth_error = "Ошибка соединения с сервером"
        self.auth_loading = False

    async def complete_registration(self):
        if not self.auth_name:
            self.auth_error = "Введите имя"
            return
        self.auth_loading = True
        self.auth_error = ""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{API_V1}/auth/register",
                    json={
                        "phone": self.auth_phone,
                        "code": self.auth_otp,
                        "first_name": self.auth_name,
                    },
                    timeout=15.0,
                )
                if resp.status_code == 201:
                    data = resp.json()
                    self.access_token = data.get("access_token", "")
                    self.refresh_token = data.get("refresh_token", "")
                    yield AppState.load_profile()
                    yield rx.redirect("/")
                else:
                    self.auth_error = resp.json().get("detail", "Ошибка регистрации")
            except Exception:
                self.auth_error = "Ошибка соединения с сервером"
        self.auth_loading = False

    def back_to_phone(self):
        self.auth_step = "phone"
        self.auth_otp = ""
        self.auth_error = ""

    def reset_auth(self):
        self.auth_step = "phone"
        self.auth_phone = ""
        self.auth_otp = ""
        self.auth_name = ""
        self.auth_email = ""
        self.auth_error = ""


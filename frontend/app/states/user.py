"""User State — profile, orders, favorites, notifications."""

import httpx
import reflex as rx

from app.api import API_V1
from app.state import AppState


class UserState(AppState):
    # Profile editing
    edit_name: str = ""
    edit_email: str = ""
    profile_loading: bool = False
    profile_error: str = ""
    profile_saved: bool = False
    profile_tab: str = "profile"  # "profile" | "garage" | "notifications"

    # Orders
    orders: list[dict] = []
    orders_loading: bool = False
    selected_order: dict = {}
    order_loading: bool = False

    # Favorites
    favorites: list[dict] = []
    favorites_loading: bool = False

    # Notifications
    notifications: list[dict] = []
    unread_count: int = 0

    async def load_orders(self):
        if not self.access_token:
            return
        self.orders_loading = True
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/orders",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.orders = data.get("items", data) if isinstance(data, dict) else data
            except Exception:
                pass
        self.orders_loading = False

    async def load_order(self, order_id: str):
        if not self.access_token:
            return
        self.order_loading = True
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/orders/{order_id}",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    self.selected_order = resp.json()
            except Exception:
                pass
        self.order_loading = False

    async def cancel_order(self, order_id: str):
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.patch(
                    f"{API_V1}/orders/{order_id}/status",
                    json={"status": "cancelled"},
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    self.selected_order = resp.json()
                    yield UserState.load_orders()
            except Exception:
                pass

    async def load_favorites(self):
        if not self.access_token:
            return
        self.favorites_loading = True
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/users/favorites",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.favorites = data.get("items", data) if isinstance(data, dict) else data
            except Exception:
                pass
        self.favorites_loading = False

    async def remove_favorite(self, partner_id: str):
        async with httpx.AsyncClient() as client:
            try:
                await client.delete(
                    f"{API_V1}/users/favorites/{partner_id}",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                self.favorites = [f for f in self.favorites if str(f.get("id")) != partner_id]
            except Exception:
                pass

    async def save_profile(self):
        self.profile_loading = True
        self.profile_error = ""
        self.profile_saved = False
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.patch(
                    f"{API_V1}/users/me",
                    json={"first_name": self.edit_name, "email": self.edit_email or None},
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    first = (data.get("first_name") or "").strip()
                    last = (data.get("last_name") or "").strip()
                    self.user_name = (first + " " + last).strip()
                    self.user_email = data.get("email", "") or ""
                    self.profile_saved = True
                else:
                    self.profile_error = resp.json().get("detail", "Ошибка сохранения")
            except Exception:
                self.profile_error = "Ошибка соединения"
        self.profile_loading = False

    async def load_notifications(self):
        if not self.access_token:
            return
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/notifications",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params={"page": 1, "size": 20},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("items", data) if isinstance(data, dict) else data
                    self.notifications = items
                    self.unread_count = sum(1 for n in items if not n.get("is_read", True))
            except Exception:
                pass

    def init_edit_profile(self):
        self.edit_name = self.user_name
        self.edit_email = self.user_email
        self.profile_saved = False
        self.profile_error = ""


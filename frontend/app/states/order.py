"""Order State — create, view, manage orders."""

import httpx
import reflex as rx

from app.api import API_V1
from app.state import AppState


class OrderState(AppState):
    # Client orders
    orders: list[dict] = []
    orders_loading: bool = False
    current_order: dict = {}
    order_detail_loading: bool = False

    # Create order
    order_partner_id: str = ""
    order_service_id: str = ""
    order_booking_id: str = ""
    order_vehicle_id: str = ""
    order_comment: str = ""
    order_loading: bool = False
    order_error: str = ""

    # Amount change
    amount_dialog_open: bool = False
    proposed_amount: str = ""
    amount_loading: bool = False

    # Partner orders
    partner_orders: list[dict] = []
    partner_orders_loading: bool = False
    partner_orders_status_filter: str = ""

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
        self.order_detail_loading = True
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/orders/{order_id}",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    self.current_order = resp.json()
            except Exception:
                pass
        self.order_detail_loading = False

    async def create_order(self):
        if not self.order_partner_id:
            self.order_error = "Партнёр не выбран"
            return
        self.order_loading = True
        self.order_error = ""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{API_V1}/orders",
                    json={
                        "partner_id": self.order_partner_id,
                        "service_id": self.order_service_id or None,
                        "booking_id": self.order_booking_id or None,
                        "vehicle_id": self.order_vehicle_id or None,
                        "comment": self.order_comment or None,
                    },
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=15.0,
                )
                if resp.status_code == 201:
                    data = resp.json()
                    yield rx.redirect(f"/orders/{data.get('id', '')}")
                else:
                    self.order_error = resp.json().get("detail", "Ошибка создания заказа")
            except Exception:
                self.order_error = "Ошибка соединения"
        self.order_loading = False

    async def update_status(self, order_id: str, new_status: str):
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.patch(
                    f"{API_V1}/orders/{order_id}/status",
                    json={"status": new_status},
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    self.current_order = resp.json()
                    yield OrderState.load_partner_orders()
            except Exception:
                pass

    async def cancel_order(self, order_id: str):
        yield OrderState.update_status(order_id, "cancelled")

    async def propose_amount(self, order_id: str):
        if not self.proposed_amount:
            return
        self.amount_loading = True
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{API_V1}/orders/{order_id}/amount-change",
                    json={"new_amount": float(self.proposed_amount)},
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    self.current_order = resp.json()
                    self.amount_dialog_open = False
                    self.proposed_amount = ""
            except Exception:
                pass
        self.amount_loading = False

    async def load_partner_orders(self):
        if not self.access_token:
            return
        self.partner_orders_loading = True
        params: dict = {}
        if self.partner_orders_status_filter:
            params["status"] = self.partner_orders_status_filter
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/orders",
                    params={**params, "role": "partner"},
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.partner_orders = data.get("items", data) if isinstance(data, dict) else data
            except Exception:
                pass
        self.partner_orders_loading = False

    async def load_order_from_url(self):
        """Извлекает order_id из URL и загружает заказ."""
        order_id = self.router.page.params.get("order_id", "")
        if order_id:
            yield OrderState.load_order(order_id)


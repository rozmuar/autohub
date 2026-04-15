"""Vehicle / Garage State."""

import httpx
import reflex as rx

from app.api import API_V1
from app.state import AppState


class VehicleState(AppState):
    vehicles: list[dict] = []
    vehicles_loading: bool = False

    add_form_open: bool = False
    new_brand: str = ""
    new_model: str = ""
    new_year: str = ""
    new_vin: str = ""
    new_license_plate: str = ""
    new_engine_type: str = "gasoline"
    new_transmission: str = "automatic"
    new_body_type: str = ""
    new_loading: bool = False
    new_error: str = ""

    # VIN lookup
    vin_raw: str = ""
    vin_loading: bool = False
    vin_error: str = ""
    vin_hint: str = ""  # decoded brand+year hint shown to user
    vin_image_url: str = ""  # Wikipedia car photo URL

    brands: list[dict] = []
    models_list: list[dict] = []

    async def load_vehicles(self):
        if not self.access_token:
            return
        self.vehicles_loading = True
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/vehicles",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.vehicles = data.get("items", data) if isinstance(data, dict) else data
            except Exception:
                pass
        self.vehicles_loading = False

    async def load_brands(self):
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"{API_V1}/vehicles/brands", timeout=10.0)
                if resp.status_code == 200:
                    data = resp.json()
                    self.brands = data.get("items", data) if isinstance(data, dict) else data
            except Exception:
                pass

    async def on_brand_change(self, brand: str):
        self.new_brand = brand
        self.new_model = ""
        self.models_list = []
        if not brand:
            return
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/vehicles/models",
                    params={"brand": brand},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.models_list = data.get("items", data) if isinstance(data, dict) else data
            except Exception:
                pass

    async def lookup_vin(self):
        vin = self.vin_raw.strip().upper()
        if len(vin) != 17:
            self.vin_error = "VIN должен содержать ровно 17 символов"
            return
        self.vin_loading = True
        self.vin_error = ""
        self.vin_hint = ""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{API_V1}/vehicles/vin/{vin}",
                    timeout=35.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if not data.get("valid"):
                        self.vin_error = "Некорректный VIN номер"
                    else:
                        self.new_vin = vin
                        vin_brand = data.get("brand")
                        vin_model = data.get("model")
                        if vin_brand:
                            # Сопоставляем с прогруженными брендами (без учёта регистра)
                            matched_brand = next(
                                (b["name"] for b in self.brands
                                 if b["name"].lower() == vin_brand.lower()),
                                vin_brand,
                            )
                            self.new_brand = matched_brand
                            # Загружаем модели для этого бренда
                            mr = await client.get(
                                f"{API_V1}/vehicles/models",
                                params={"brand": matched_brand},
                                timeout=10.0,
                            )
                            if mr.status_code == 200:
                                mdata = mr.json()
                                self.models_list = mdata.get("items", mdata) if isinstance(mdata, dict) else mdata
                        if vin_model:
                            self.new_model = vin_model
                        if data.get("year"):
                            self.new_year = str(data["year"])
                        if data.get("engine_type"):
                            self.new_engine_type = data["engine_type"]
                        if data.get("transmission"):
                            self.new_transmission = data["transmission"]
                        if data.get("body_class"):
                            self.new_body_type = data["body_class"]
                        self.vin_image_url = data.get("image_url") or ""
                        parts = []
                        if vin_brand:
                            parts.append(self.new_brand)
                        if vin_model:
                            parts.append(vin_model)
                        if data.get("year"):
                            parts.append(str(data["year"]) + " г.")
                        if data.get("country"):
                            parts.append(data["country"])
                        self.vin_hint = " · ".join(parts) if parts else "VIN распознан"
                else:
                    self.vin_error = "Не удалось декодировать VIN"
            except Exception:
                self.vin_error = "Ошибка соединения"
        self.vin_loading = False

    async def add_vehicle(self):
        if not self.access_token:
            self.new_error = "Необходимо войти в аккаунт"
            return
        if not self.new_brand or not self.new_model:
            self.new_error = "Укажите марку и модель"
            return
        if not self.new_year or not self.new_year.isdigit():
            self.new_error = "Укажите год выпуска"
            return
        self.new_loading = True
        self.new_error = ""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{API_V1}/vehicles",
                    json={
                        "brand_name": self.new_brand,
                        "model_name": self.new_model,
                        "year": int(self.new_year),
                        "vin": self.new_vin or None,
                        "plate_number": self.new_license_plate or None,
                        "engine_type": self.new_engine_type or None,
                        "transmission": self.new_transmission or None,
                        "body_type": self.new_body_type or None,
                        "vin_decoded": bool(self.new_vin),
                    },
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 201:
                    self.vehicles = [*self.vehicles, resp.json()]
                    self.add_form_open = False
                    self.new_brand = ""
                    self.new_model = ""
                    self.new_year = ""
                    self.new_vin = ""
                    self.new_license_plate = ""
                    self.new_body_type = ""
                    self.vin_raw = ""
                    self.vin_hint = ""
                    self.vin_image_url = ""
                    self.vin_error = ""
                else:
                    try:
                        detail = resp.json().get("detail", "Ошибка добавления")
                        if isinstance(detail, list):
                            self.new_error = detail[0].get("msg", "Ошибка добавления") if detail else "Ошибка добавления"
                        else:
                            self.new_error = str(detail)
                    except Exception:
                        self.new_error = f"Ошибка {resp.status_code}"
            except httpx.ConnectError:
                self.new_error = "Нет связи с сервером"
            except httpx.TimeoutException:
                self.new_error = "Превышено время ожидания"
            except Exception as e:
                self.new_error = f"Ошибка: {type(e).__name__}: {e}"
        self.new_loading = False

    async def delete_vehicle(self, vehicle_id: str):
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.delete(
                    f"{API_V1}/vehicles/{vehicle_id}",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 204:
                    self.vehicles = [v for v in self.vehicles if str(v.get("id")) != vehicle_id]
            except Exception:
                pass

    async def open_add_form(self):
        self.add_form_open = True
        self.new_error = ""
        self.vin_raw = ""
        self.vin_hint = ""
        self.vin_image_url = ""
        self.vin_error = ""
        self.new_vin = ""
        self.new_body_type = ""
        self.new_error = ""
        if not self.brands:
            await self.load_brands()


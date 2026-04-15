"""Страница гаража — список автомобилей пользователя."""

import reflex as rx

from app.components.navbar import navbar
from app.states.vehicle import VehicleState


_ENGINE_OPTIONS = ["gasoline", "diesel", "electric", "hybrid", "gas"]
_TRANS_OPTIONS = ["automatic", "manual", "robot", "variator"]

_ENGINE_LABELS = {
    "gasoline": "Бензин",
    "diesel": "Дизель",
    "electric": "Электро",
    "hybrid": "Гибрид",
    "gas": "Газ",
}

_TRANS_LABELS = {
    "automatic": "Автомат",
    "manual": "Механика",
    "robot": "Робот",
    "variator": "Вариатор",
}


def _vehicle_card(v: rx.Var) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.box(
                rx.icon("car", size=32, color="blue"),
                background="#eff6ff",
                border_radius="12px",
                padding="16px",
            ),
            rx.vstack(
                rx.text(
                    rx.text(v["brand"], " ", v["model"]),
                    font_weight="600",
                    size="4",
                ),
                rx.hstack(
                    rx.badge(v["year"].to_string(), size="1", variant="soft"),
                    rx.badge(v["engine_type"], size="1", variant="soft", color_scheme="cyan"),
                    rx.badge(v["transmission"], size="1", variant="soft", color_scheme="purple"),
                    spacing="1",
                    flex_wrap="wrap",
                ),
                rx.cond(
                    v["license_plate"] != "",
                    rx.text(v["license_plate"], size="2", color="gray", font_family="monospace"),
                ),
                spacing="1",
                align_items="start",
            ),
            rx.spacer(),
            rx.button(
                rx.icon("trash-2", size=14),
                color_scheme="red",
                variant="ghost",
                size="2",
                on_click=VehicleState.delete_vehicle(v["id"].to_string()),
            ),
            align="center",
            width="100%",
        ),
        width="100%",
    )


def _add_form() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=16),
                "Добавить автомобиль",
                color_scheme="blue",
                size="2",
            ),
        ),
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title("Новый автомобиль"),
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text("Марка", size="2", color="gray"),
                            rx.input(
                                placeholder="Toyota",
                                value=VehicleState.new_brand,
                                on_change=VehicleState.set_new_brand,
                                size="2",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Модель", size="2", color="gray"),
                            rx.input(
                                placeholder="Camry",
                                value=VehicleState.new_model,
                                on_change=VehicleState.set_new_model,
                                size="2",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Год", size="2", color="gray"),
                            rx.input(
                                placeholder="2020",
                                value=VehicleState.new_year,
                                on_change=VehicleState.set_new_year,
                                type="number",
                                size="2",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Госномер", size="2", color="gray"),
                            rx.input(
                                placeholder="А001АА177",
                                value=VehicleState.new_license_plate,
                                on_change=VehicleState.set_new_license_plate,
                                size="2",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Двигатель", size="2", color="gray"),
                            rx.select.root(
                                rx.select.trigger(placeholder="Тип двигателя"),
                                rx.select.content(
                                    rx.select.item("Бензин", value="gasoline"),
                                    rx.select.item("Дизель", value="diesel"),
                                    rx.select.item("Электро", value="electric"),
                                    rx.select.item("Гибрид", value="hybrid"),
                                    rx.select.item("Газ", value="gas"),
                                ),
                                value=VehicleState.new_engine_type,
                                on_change=VehicleState.set_new_engine_type,
                                size="2",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Трансмиссия", size="2", color="gray"),
                            rx.select.root(
                                rx.select.trigger(placeholder="Тип КПП"),
                                rx.select.content(
                                    rx.select.item("Автомат", value="automatic"),
                                    rx.select.item("Механика", value="manual"),
                                    rx.select.item("Робот", value="robot"),
                                    rx.select.item("Вариатор", value="variator"),
                                ),
                                value=VehicleState.new_transmission,
                                on_change=VehicleState.set_new_transmission,
                                size="2",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.input(
                        placeholder="VIN (необязательно)",
                        value=VehicleState.new_vin,
                        on_change=VehicleState.set_new_vin,
                        size="2",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                rx.cond(
                    VehicleState.new_error != "",
                    rx.text(VehicleState.new_error, color="red", size="2"),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Отмена", variant="outline", size="2"),
                    ),
                    rx.button(
                        "Добавить",
                        on_click=VehicleState.add_vehicle,
                        loading=VehicleState.new_loading,
                        color_scheme="blue",
                        size="2",
                    ),
                    justify="end",
                    spacing="2",
                ),
                spacing="4",
                width="100%",
            ),
            max_width="520px",
        ),
    )


def garage_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.container(
            rx.vstack(
                rx.hstack(
                    rx.heading("Мой гараж", size="7"),
                    rx.spacer(),
                    _add_form(),
                    align="center",
                    width="100%",
                ),
                rx.cond(
                    VehicleState.vehicles_loading,
                    rx.center(rx.spinner(size="3"), padding="3em"),
                    rx.cond(
                        VehicleState.vehicles,
                        rx.vstack(
                            rx.foreach(VehicleState.vehicles, _vehicle_card),
                            spacing="3",
                            width="100%",
                        ),
                        rx.center(
                            rx.vstack(
                                rx.icon("car", size=48, color="gray"),
                                rx.text("В гараже пусто", size="4", color="gray"),
                                rx.text("Добавьте свой первый автомобиль", size="3", color="gray"),
                                spacing="2",
                                align="center",
                            ),
                            padding="4em",
                        ),
                    ),
                ),
                spacing="6",
                width="100%",
                padding_y="2em",
            ),
            max_width="800px",
        ),
        on_mount=VehicleState.load_vehicles,
    )



"""Управление услугами партнёра."""

import reflex as rx

from app.components.navbar import navbar
from app.states.partner import PartnerState


def _service_row(svc: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(svc["name"], font_weight="500", size="3"),
            rx.cond(
                svc["description"],
                rx.text(svc["description"], size="2", color="gray"),
            ),
            spacing="1",
            align_items="start",
        ),
        rx.badge(
            rx.cond(svc["category_name"], svc["category_name"], "Без категории"),
            size="1",
            variant="soft",
        ),
        rx.spacer(),
        rx.text(
            rx.cond(
                svc["price"],
                rx.text(svc["price"].to_string(), " ₽"),
                "По запросу",
            ),
            font_weight="600",
            size="3",
        ),
        rx.text(
            rx.cond(
                svc["duration_minutes"],
                rx.text(svc["duration_minutes"].to_string(), " мин"),
                "",
            ),
            size="2",
            color="gray",
            min_width="50px",
            text_align="right",
        ),
        rx.button(
            rx.icon("trash-2", size=14),
            variant="ghost",
            color_scheme="red",
            size="1",
            on_click=PartnerState.delete_service(svc["id"].to_string()),
        ),
        align="center",
        width="100%",
        padding_y="0.75em",
    )


def _add_service_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=16),
                "Добавить услугу",
                color_scheme="blue",
                size="2",
            ),
        ),
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title("Новая услуга"),
                rx.vstack(
                    rx.vstack(
                        rx.text("Название", size="2", color="gray"),
                        rx.input(
                            placeholder="Замена масла, шиномонтаж...",
                            value=PartnerState.svc_name,
                            on_change=PartnerState.set_svc_name,
                            size="2",
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Цена (₽)", size="2", color="gray"),
                            rx.input(
                                placeholder="1500",
                                value=PartnerState.svc_price,
                                on_change=PartnerState.set_svc_price,
                                type="number",
                                size="2",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Длительность (мин)", size="2", color="gray"),
                            rx.input(
                                placeholder="60",
                                value=PartnerState.svc_duration.to_string(),
                                on_change=PartnerState.set_svc_duration,
                                type="number",
                                size="2",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Описание (необязательно)", size="2", color="gray"),
                        rx.text_area(
                            placeholder="Что включает услуга...",
                            value=PartnerState.svc_description,
                            on_change=PartnerState.set_svc_description,
                            rows="3",
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                rx.cond(
                    PartnerState.svc_error != "",
                    rx.text(PartnerState.svc_error, color="red", size="2"),
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Отмена", variant="outline", size="2"),
                    ),
                    rx.button(
                        "Добавить",
                        on_click=PartnerState.add_service,
                        loading=PartnerState.svc_loading,
                        color_scheme="blue",
                        size="2",
                    ),
                    justify="end",
                    spacing="2",
                ),
                spacing="4",
                width="100%",
            ),
            max_width="500px",
        ),
    )


def partner_services_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.container(
            rx.vstack(
                rx.hstack(
                    rx.heading("Мои услуги", size="7"),
                    rx.spacer(),
                    _add_service_dialog(),
                    align="center",
                    width="100%",
                ),
                rx.card(
                    rx.cond(
                        PartnerState.services,
                        rx.vstack(
                            rx.foreach(PartnerState.services, _service_row),
                            spacing="0",
                            divide_y="1px solid #e5e7eb",
                            width="100%",
                        ),
                        rx.center(
                            rx.vstack(
                                rx.icon("package", size=40, color="gray"),
                                rx.text("Услуг пока нет", size="4", color="gray"),
                                rx.text(
                                    "Добавьте услуги, чтобы клиенты могли вас найти",
                                    size="3",
                                    color="gray",
                                ),
                                spacing="2",
                                align="center",
                            ),
                            padding="3em",
                        ),
                    ),
                    width="100%",
                    padding="1.5em",
                ),
                spacing="5",
                padding_y="2em",
                width="100%",
            ),
            max_width="900px",
        ),
        on_mount=PartnerState.load_services,
    )


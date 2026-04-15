"""Заказы партнёра — управление."""

import reflex as rx

from app.components.navbar import navbar
from app.components.order_card import status_badge
from app.states.order import OrderState


_STATUSES = [
    ("", "Все"),
    ("pending", "Ожидают"),
    ("confirmed", "Подтверждённые"),
    ("in_progress", "В работе"),
    ("completed", "Завершённые"),
    ("cancelled", "Отменённые"),
]


def _status_filter() -> rx.Component:
    return rx.hstack(
        *[
            rx.button(
                label,
                variant=rx.cond(
                    OrderState.partner_orders_status_filter == val,
                    "solid",
                    "outline",
                ),
                color_scheme=rx.cond(
                    OrderState.partner_orders_status_filter == val,
                    "blue",
                    "gray",
                ),
                size="2",
                on_click=OrderState.set_partner_orders_status_filter(val),
            )
            for val, label in _STATUSES
        ],
        flex_wrap="wrap",
        spacing="2",
    )


def _order_row(order: rx.Var) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.text(
                        rx.text("Заказ #", order["id"].to_string()),
                        font_weight="600",
                        size="3",
                    ),
                    status_badge(order["status"]),
                    spacing="2",
                    align="center",
                ),
                rx.text(
                    rx.cond(order["client_name"], order["client_name"], "Клиент"),
                    size="2",
                    color="gray",
                ),
                rx.cond(
                    order["service_name"],
                    rx.text(order["service_name"], size="2"),
                ),
                spacing="1",
                align_items="start",
            ),
            rx.spacer(),
            rx.vstack(
                rx.cond(
                    order["total_amount"],
                    rx.text(
                        rx.text(order["total_amount"].to_string(), " ₽"),
                        font_weight="700",
                        size="4",
                    ),
                ),
                rx.text(
                    rx.cond(order["created_at"], order["created_at"], ""),
                    size="1",
                    color="gray",
                ),
                align_items="end",
                spacing="1",
            ),
            rx.vstack(
                # Кнопки смены статуса
                rx.cond(
                    order["status"] == "pending",
                    rx.hstack(
                        rx.button(
                            "Принять",
                            color_scheme="green",
                            size="1",
                            on_click=OrderState.update_status(order["id"].to_string(), "confirmed"),
                        ),
                        rx.button(
                            "Отклонить",
                            color_scheme="red",
                            variant="soft",
                            size="1",
                            on_click=OrderState.update_status(order["id"].to_string(), "cancelled"),
                        ),
                        spacing="1",
                    ),
                ),
                rx.cond(
                    order["status"] == "confirmed",
                    rx.button(
                        "Начать работу",
                        color_scheme="blue",
                        size="1",
                        on_click=OrderState.update_status(order["id"].to_string(), "in_progress"),
                    ),
                ),
                rx.cond(
                    order["status"] == "in_progress",
                    rx.button(
                        "Завершить",
                        color_scheme="green",
                        size="1",
                        on_click=OrderState.update_status(order["id"].to_string(), "completed"),
                    ),
                ),
                spacing="1",
            ),
            align="center",
            width="100%",
            spacing="3",
        ),
        width="100%",
    )


def partner_orders_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Заказы", size="7"),
                _status_filter(),
                rx.cond(
                    OrderState.partner_orders_loading,
                    rx.center(rx.spinner(size="3"), padding="3em"),
                    rx.cond(
                        OrderState.partner_orders,
                        rx.vstack(
                            rx.foreach(OrderState.partner_orders, _order_row),
                            spacing="3",
                            width="100%",
                        ),
                        rx.center(
                            rx.vstack(
                                rx.icon("inbox", size=48, color="gray"),
                                rx.text("Заказов нет", size="4", color="gray"),
                                spacing="2",
                                align="center",
                            ),
                            padding="4em",
                        ),
                    ),
                ),
                spacing="5",
                padding_y="2em",
                width="100%",
            ),
            max_width="1000px",
        ),
        on_mount=OrderState.load_partner_orders,
    )


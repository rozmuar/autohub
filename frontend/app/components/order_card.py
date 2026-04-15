"""Карточка заказа."""

import reflex as rx


_STATUS_LABEL = {
    "pending": "Ожидает",
    "confirmed": "Подтверждён",
    "in_progress": "В работе",
    "completed": "Завершён",
    "cancelled": "Отменён",
    "payment_pending": "Ожидает оплаты",
}

_STATUS_COLOR = {
    "pending": "orange",
    "confirmed": "blue",
    "in_progress": "cyan",
    "completed": "green",
    "cancelled": "red",
    "payment_pending": "amber",
}


def status_badge(status: rx.Var) -> rx.Component:
    return rx.match(
        status,
        ("pending", rx.badge("Ожидает", color_scheme="orange", size="1")),
        ("confirmed", rx.badge("Подтверждён", color_scheme="blue", size="1")),
        ("in_progress", rx.badge("В работе", color_scheme="cyan", size="1")),
        ("completed", rx.badge("Завершён", color_scheme="green", size="1")),
        ("cancelled", rx.badge("Отменён", color_scheme="red", size="1")),
        ("payment_pending", rx.badge("Ожидает оплаты", color_scheme="amber", size="1")),
        rx.badge(status, color_scheme="gray", size="1"),
    )


def order_card(order: rx.Var, on_click=None) -> rx.Component:
    """Карточка/строка заказа."""
    card = rx.card(
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
                    rx.cond(
                        order["partner_name"],
                        order["partner_name"],
                        "Партнёр",
                    ),
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
                        font_weight="600",
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
            align="center",
            width="100%",
        ),
        width="100%",
        cursor=rx.cond(on_click is not None, "pointer", "default"),
        _hover={"box_shadow": "0 2px 8px rgba(0,0,0,0.08)"},
    )

    if on_click is not None:
        return rx.box(card, on_click=on_click, width="100%")
    return card


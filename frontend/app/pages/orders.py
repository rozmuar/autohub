"""Страница заказов пользователя."""

import reflex as rx

from app.components.navbar import navbar
from app.components.order_card import order_card, status_badge
from app.states.user import UserState
from app.states.order import OrderState
from app.state import AppState


def _order_detail_view() -> rx.Component:
    order = OrderState.current_order
    return rx.vstack(
        rx.hstack(
            rx.button(
                rx.icon("arrow-left", size=16),
                "Назад к заказам",
                variant="ghost",
                size="2",
                on_click=rx.redirect("/orders"),
            ),
        ),
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading(
                        rx.text("Заказ #", order["id"].to_string()),
                        size="5",
                    ),
                    status_badge(order["status"]),
                    spacing="3",
                    align="center",
                ),
                rx.separator(width="100%"),
                rx.grid(
                    rx.vstack(
                        rx.text("Партнёр", size="2", color="gray"),
                        rx.text(order["partner_name"], size="3", font_weight="500"),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Услуга", size="2", color="gray"),
                        rx.text(
                            rx.cond(order["service_name"], order["service_name"], "—"),
                            size="3",
                        ),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Автомобиль", size="2", color="gray"),
                        rx.text(
                            rx.cond(order["vehicle_info"], order["vehicle_info"], "—"),
                            size="3",
                        ),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Сумма", size="2", color="gray"),
                        rx.text(
                            rx.cond(
                                order["total_amount"],
                                rx.text(order["total_amount"].to_string(), " ₽"),
                                "—",
                            ),
                            size="4",
                            font_weight="700",
                            color="blue",
                        ),
                        spacing="1",
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                rx.cond(
                    order["comment"],
                    rx.vstack(
                        rx.text("Комментарий", size="2", color="gray"),
                        rx.text(order["comment"], size="3"),
                        spacing="1",
                        width="100%",
                    ),
                ),
                # Кнопки действий
                rx.hstack(
                    rx.cond(
                        order["status"] == "pending",
                        rx.button(
                            "Отменить заказ",
                            color_scheme="red",
                            variant="soft",
                            size="2",
                            on_click=OrderState.cancel_order(order["id"].to_string()),
                        ),
                    ),
                    rx.cond(
                        order["status"] == "completed",
                        rx.link(
                            rx.button(
                                rx.icon("star", size=14),
                                "Оставить отзыв",
                                variant="outline",
                                size="2",
                            ),
                            href="/review/" + order["id"].to_string(),
                        ),
                    ),
                    rx.cond(
                        order["partner_user_id"],
                        rx.button(
                            rx.icon("message-circle", size=14),
                            "Написать партнёру",
                            variant="outline",
                            size="2",
                            on_click=rx.redirect("/chat"),
                        ),
                    ),
                    spacing="2",
                    flex_wrap="wrap",
                ),
                spacing="4",
                width="100%",
            ),
            width="100%",
            padding="1.5em",
        ),
        spacing="4",
        width="100%",
    )


def orders_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Мои заказы", size="7"),
                rx.cond(
                    UserState.orders_loading,
                    rx.center(rx.spinner(size="3"), padding="3em"),
                    rx.cond(
                        UserState.orders,
                        rx.vstack(
                            rx.foreach(
                                UserState.orders,
                                lambda o: order_card(
                                    o,
                                    on_click=rx.redirect("/orders/" + o["id"].to_string()),
                                ),
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        rx.center(
                            rx.vstack(
                                rx.icon("package-open", size=48, color="gray"),
                                rx.text("Заказов пока нет", size="4", color="gray"),
                                rx.link(
                                    rx.button("Найти партнёра", color_scheme="blue"),
                                    href="/search",
                                ),
                                spacing="3",
                                align="center",
                            ),
                            padding="4em",
                        ),
                    ),
                ),
                spacing="6",
                padding_y="2em",
                width="100%",
            ),
            max_width="800px",
        ),
        on_mount=UserState.load_orders,
    )


def order_detail_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.container(
            rx.cond(
                OrderState.order_detail_loading,
                rx.center(rx.spinner(size="3"), padding="3em"),
                _order_detail_view(),
            ),
            max_width="800px",
            padding_y="2em",
        ),
    )


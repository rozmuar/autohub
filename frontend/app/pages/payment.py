"""Страница оплаты заказа."""

import reflex as rx

from app.components.navbar import navbar
from app.state import AppState


def payment_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.container(
            rx.center(
                rx.card(
                    rx.vstack(
                        rx.icon("credit-card", size=48, color="blue"),
                        rx.heading("Оплата заказа", size="5"),
                        rx.text(
                            "Выберите способ оплаты",
                            size="3",
                            color="gray",
                            text_align="center",
                        ),
                        rx.vstack(
                            rx.card(
                                rx.hstack(
                                    rx.icon("credit-card", size=20, color="blue"),
                                    rx.text("Банковская карта", size="3", font_weight="500"),
                                    rx.spacer(),
                                    rx.icon("arrow-right", size=16, color="gray"),
                                    align="center",
                                    width="100%",
                                ),
                                width="100%",
                                cursor="pointer",
                                _hover={"background": "#f8fafc"},
                            ),
                            rx.card(
                                rx.hstack(
                                    rx.icon("smartphone", size=20, color="green"),
                                    rx.text("СБП (Система быстрых платежей)", size="3", font_weight="500"),
                                    rx.spacer(),
                                    rx.icon("arrow-right", size=16, color="gray"),
                                    align="center",
                                    width="100%",
                                ),
                                width="100%",
                                cursor="pointer",
                                _hover={"background": "#f8fafc"},
                            ),
                            rx.card(
                                rx.hstack(
                                    rx.icon("banknote", size=20, color="amber"),
                                    rx.text("Наличными при получении", size="3", font_weight="500"),
                                    rx.spacer(),
                                    rx.icon("arrow-right", size=16, color="gray"),
                                    align="center",
                                    width="100%",
                                ),
                                width="100%",
                                cursor="pointer",
                                _hover={"background": "#f8fafc"},
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.link(
                            rx.button("← Назад к заказу", variant="ghost", size="2"),
                            href="/orders",
                        ),
                        spacing="5",
                        align="center",
                        width="100%",
                    ),
                    max_width="440px",
                    width="100%",
                    padding="2em",
                ),
                min_height="80vh",
            ),
            max_width="600px",
        ),
    )


def payment_success_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.center(
            rx.card(
                rx.vstack(
                    rx.icon("circle-check", size=64, color="green"),
                    rx.heading("Оплата прошла успешно!", size="5"),
                    rx.text("Спасибо за оплату. Ваш заказ принят в работу.", size="3", color="gray"),
                    rx.link(
                        rx.button("Мои заказы", color_scheme="blue", size="3"),
                        href="/orders",
                    ),
                    spacing="4",
                    align="center",
                ),
                max_width="400px",
                width="100%",
                padding="3em",
            ),
            min_height="90vh",
        ),
    )


def payment_fail_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.center(
            rx.card(
                rx.vstack(
                    rx.icon("circle-x", size=64, color="red"),
                    rx.heading("Оплата не прошла", size="5"),
                    rx.text("Произошла ошибка при оплате. Попробуйте ещё раз.", size="3", color="gray"),
                    rx.hstack(
                        rx.link(
                            rx.button("Попробовать снова", color_scheme="blue", size="3"),
                            href="/payment",
                        ),
                        rx.link(
                            rx.button("Мои заказы", variant="outline", size="3"),
                            href="/orders",
                        ),
                        spacing="3",
                    ),
                    spacing="4",
                    align="center",
                ),
                max_width="400px",
                width="100%",
                padding="3em",
            ),
            min_height="90vh",
        ),
    )


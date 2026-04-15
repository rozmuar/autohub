"""Дашборд партнёра."""

import reflex as rx

from app.components.navbar import navbar
from app.components.order_card import order_card, status_badge
from app.states.partner import PartnerState
from app.states.order import OrderState


def _stat_card(title: str, value: rx.Var, icon: str, color: str = "blue") -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=20, color=color),
                rx.text(title, size="2", color="gray"),
                spacing="2",
                align="center",
            ),
            rx.text(value, size="7", font_weight="700", color=color),
            spacing="2",
        ),
        padding="1.5em",
    )


def partner_dashboard() -> rx.Component:
    profile = PartnerState.partner_profile
    return rx.fragment(
        navbar(),
        rx.container(
            rx.vstack(
                # Шапка
                rx.hstack(
                    rx.vstack(
                        rx.heading("Кабинет партнёра", size="7"),
                        rx.cond(
                            profile,
                            rx.text(
                                rx.text("Добро пожаловать, ", profile["company_name"]),
                                size="3",
                                color="gray",
                            ),
                        ),
                        align_items="start",
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.link(
                            rx.button("Услуги", variant="outline", size="2"),
                            href="/partner/services",
                        ),
                        rx.link(
                            rx.button("Расписание", variant="outline", size="2"),
                            href="/partner/schedule",
                        ),
                        rx.link(
                            rx.button("Аналитика", variant="outline", size="2"),
                            href="/partner/analytics",
                        ),
                        spacing="2",
                    ),
                    align="center",
                    width="100%",
                ),
                rx.cond(
                    PartnerState.partner_loading,
                    rx.center(rx.spinner(size="3"), padding="3em"),
                    rx.vstack(
                        # Статистика
                        rx.grid(
                            _stat_card(
                                "Всего заказов",
                                profile["orders_count"].to_string(),
                                "package",
                                "blue",
                            ),
                            _stat_card(
                                "Выручка",
                                rx.text(profile["revenue"].to_string(), " ₽"),
                                "trending-up",
                                "green",
                            ),
                            _stat_card(
                                "Рейтинг",
                                profile["rating"].to_string(),
                                "star",
                                "amber",
                            ),
                            _stat_card(
                                "Отзывов",
                                profile["reviews_count"].to_string(),
                                "message-square",
                                "purple",
                            ),
                            columns="4",
                            spacing="4",
                            width="100%",
                        ),
                        # Последние заказы
                        rx.vstack(
                            rx.hstack(
                                rx.heading("Последние заказы", size="5"),
                                rx.spacer(),
                                rx.link(
                                    rx.button("Все заказы →", variant="ghost", size="2"),
                                    href="/partner/orders",
                                ),
                                align="center",
                                width="100%",
                            ),
                            rx.cond(
                                OrderState.partner_orders,
                                rx.vstack(
                                    rx.foreach(
                                        OrderState.partner_orders,
                                        lambda o: order_card(
                                            o,
                                            on_click=rx.redirect(
                                                rx.text("/partner/orders/", o["id"].to_string())
                                            ),
                                        ),
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                rx.text("Нет заказов", size="3", color="gray"),
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        spacing="6",
                        width="100%",
                    ),
                ),
                spacing="6",
                padding_y="2em",
                width="100%",
            ),
            max_width="1100px",
        ),
        on_mount=[PartnerState.load_partner_profile, OrderState.load_partner_orders],
    )



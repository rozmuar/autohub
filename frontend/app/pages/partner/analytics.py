"""Аналитика партнёра — Phase 2."""

import reflex as rx

from app.components.navbar import navbar
from app.states.partner import PartnerState
from app.state import AppState


def _metric_card(title: str, value: rx.Var, subtitle: str = "", color: str = "blue") -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(title, size="2", color="gray"),
            rx.text(value, size="7", font_weight="700", color=color),
            rx.cond(
                subtitle,
                rx.text(subtitle, size="2", color="gray"),
            ),
            spacing="2",
        ),
        padding="1.5em",
    )


def partner_analytics_page() -> rx.Component:
    data = PartnerState.analytics_data
    return rx.fragment(
        navbar(),
        rx.container(
            rx.vstack(
                rx.hstack(
                    rx.heading("Аналитика", size="7"),
                    rx.spacer(),
                    # Фильтр по дате
                    rx.hstack(
                        rx.input(
                            type="date",
                            value=PartnerState.analytics_date_from,
                            on_change=PartnerState.set_analytics_date_from,
                            size="2",
                        ),
                        rx.text("—", size="2"),
                        rx.input(
                            type="date",
                            value=PartnerState.analytics_date_to,
                            on_change=PartnerState.set_analytics_date_to,
                            size="2",
                        ),
                        rx.button(
                            "Обновить",
                            on_click=PartnerState.load_analytics,
                            loading=PartnerState.analytics_loading,
                            size="2",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    align="center",
                    width="100%",
                ),
                rx.cond(
                    PartnerState.analytics_loading,
                    rx.center(rx.spinner(size="3"), padding="3em"),
                    rx.cond(
                        PartnerState.analytics_data,
                        rx.vstack(
                            # Ключевые метрики
                            rx.grid(
                                _metric_card(
                                    "Выручка",
                                    rx.text(data["revenue"].to_string(), " ₽"),
                                    "за период",
                                    "green",
                                ),
                                _metric_card(
                                    "Заказов",
                                    data["orders_count"].to_string(),
                                    "за период",
                                    "blue",
                                ),
                                _metric_card(
                                    "Средний чек",
                                    rx.text(data["avg_order_value"].to_string(), " ₽"),
                                    "",
                                    "purple",
                                ),
                                _metric_card(
                                    "Рейтинг",
                                    data["avg_rating"].to_string(),
                                    rx.text(data["reviews_count"].to_string(), " отзывов"),
                                    "amber",
                                ),
                                columns="4",
                                spacing="4",
                                width="100%",
                            ),
                            # Топ услуг
                            rx.cond(
                                PartnerState.top_services,
                                rx.card(
                                    rx.vstack(
                                        rx.heading("Популярные услуги", size="4"),
                                        rx.separator(width="100%"),
                                        rx.foreach(
                                            PartnerState.top_services,
                                            lambda s: rx.hstack(
                                                rx.text(s["name"], size="3", flex="1"),
                                                rx.text(
                                                    s["orders_count"].to_string(), " заказов",
                                                    size="2",
                                                    color="gray",
                                                ),
                                                rx.text(
                                                    s["revenue"].to_string(), " ₽",
                                                    font_weight="600",
                                                    size="3",
                                                ),
                                                align="center",
                                                width="100%",
                                                padding_y="0.5em",
                                            ),
                                        ),
                                        spacing="2",
                                        width="100%",
                                    ),
                                    padding="1.5em",
                                    width="100%",
                                ),
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        rx.center(
                            rx.vstack(
                                rx.icon("bar-chart-2", size=48, color="gray"),
                                rx.text("Выберите период для просмотра аналитики", size="4", color="gray"),
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
            max_width="1100px",
        ),
    )


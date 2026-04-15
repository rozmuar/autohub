"""Карточка партнёра для результатов поиска."""

import reflex as rx

from app.components.star_rating import star_rating


_STATUS_COLORS = {
    "active": "green",
    "inactive": "gray",
    "pending": "orange",
}


def partner_card(partner: rx.Var) -> rx.Component:
    """Карточка партнёра в поисковой выдаче."""
    return rx.card(
        rx.vstack(
            # Заголовок: логотип + название
            rx.hstack(
                rx.cond(
                    partner["logo_url"],
                    rx.image(
                        src=partner["logo_url"],
                        width="48px",
                        height="48px",
                        border_radius="8px",
                        object_fit="cover",
                    ),
                    rx.box(
                        rx.icon("wrench", size=24, color="blue"),
                        background="#eff6ff",
                        border_radius="8px",
                        padding="12px",
                    ),
                ),
                rx.vstack(
                    rx.text(partner["company_name"], font_weight="600", size="4"),
                    rx.hstack(
                        star_rating(partner["rating"]),
                        rx.text(partner["rating"], size="2", color="gray"),
                        rx.cond(
                            partner["reviews_count"],
                            rx.text("(", partner["reviews_count"], " отзывов)", size="2", color="gray"),
                        ),
                        spacing="1",
                        align="center",
                    ),
                    spacing="1",
                    align_items="start",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            # Адрес
            rx.hstack(
                rx.icon("map-pin", size=14, color="gray"),
                rx.text(partner["address"], size="2", color="gray"),
                spacing="1",
            ),
            # Категории (показываем только если есть)
            rx.cond(
                partner["categories"],
                rx.badge("Услуги доступны", size="1", variant="soft", color_scheme="blue"),
            ),
            # Кнопки действий
            rx.hstack(
                rx.link(
                    rx.button("Подробнее", variant="outline", size="2"),
                    href="/partners/" + partner["id"].to_string(),
                ),
                rx.link(
                    rx.button("Записаться", color_scheme="blue", size="2"),
                    href="/booking?partner=" + partner["id"].to_string(),
                ),
                justify="end",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
        _hover={"box_shadow": "0 4px 12px rgba(0,0,0,0.1)"},
        cursor="default",
    )


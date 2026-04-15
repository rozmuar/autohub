"""Страница детали партнёра."""

import reflex as rx

from app.components.navbar import navbar
from app.components.star_rating import star_rating
from app.states.search import SearchState
from app.state import AppState


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
        rx.spacer(),
        rx.vstack(
            rx.cond(
                svc["price"],
                rx.text(svc["price"].to_string(), " ₽", font_weight="600", size="3"),
                rx.text("По запросу", font_weight="600", size="3"),
            ),
            rx.cond(
                svc["duration_minutes"],
                rx.text(svc["duration_minutes"].to_string(), " мин", size="2", color="gray"),
            ),
            align_items="end",
            spacing="1",
        ),
        align="center",
        width="100%",
        padding_y="0.5em",
    )


def _review_card(review: rx.Var) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("user-circle", size=20, color="gray"),
                rx.text(review["author_name"], font_weight="500", size="3"),
                rx.spacer(),
                star_rating(review["rating"], size=14),
                align="center",
                width="100%",
            ),
            rx.text(
                rx.cond(review["text"], review["text"], ""),
                size="2",
                color="gray",
            ),
            rx.cond(
                review["partner_reply"],
                rx.box(
                    rx.vstack(
                        rx.text("Ответ партнёра:", size="2", font_weight="600", color="blue"),
                        rx.text(review["partner_reply"], size="2"),
                        spacing="1",
                    ),
                    background="#eff6ff",
                    padding="0.75em",
                    border_radius="6px",
                    width="100%",
                ),
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def partner_detail_page() -> rx.Component:
    partner = SearchState.selected_partner
    return rx.fragment(
        navbar(),
        rx.container(
            rx.cond(
                SearchState.partner_loading,
                rx.center(rx.spinner(size="3"), padding="4em"),
                rx.vstack(
                    # Шапка
                    rx.card(
                        rx.hstack(
                            rx.cond(
                                partner["logo_url"],
                                rx.image(
                                    src=partner["logo_url"],
                                    width="80px",
                                    height="80px",
                                    border_radius="12px",
                                    object_fit="cover",
                                ),
                                rx.box(
                                    rx.icon("wrench", size=40, color="blue"),
                                    background="#eff6ff",
                                    border_radius="12px",
                                    padding="20px",
                                ),
                            ),
                            rx.vstack(
                                rx.heading(partner["company_name"], size="6"),
                                rx.hstack(
                                    star_rating(partner["rating"]),
                                    rx.text(partner["rating"].to_string(), size="2"),
                                    rx.text("(", partner["reviews_count"].to_string(), " отзывов)", size="2", color="gray"),
                                    spacing="2",
                                    align="center",
                                ),
                                rx.hstack(
                                    rx.icon("map-pin", size=14, color="gray"),
                                    rx.text(partner["address"], size="3", color="gray"),
                                    spacing="1",
                                ),
                                rx.cond(
                                    partner["phone"],
                                    rx.hstack(
                                        rx.icon("phone", size=14, color="gray"),
                                        rx.text(partner["phone"], size="3", color="gray"),
                                        spacing="1",
                                    ),
                                ),
                                align_items="start",
                                spacing="2",
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.cond(
                                    AppState.is_authenticated,
                                    rx.link(
                                        rx.button("Записаться", color_scheme="blue", size="3"),
                                        href="/booking",
                                    ),
                                    rx.link(
                                        rx.button("Войти и записаться", color_scheme="blue", size="3"),
                                        href="/login",
                                    ),
                                ),
                                rx.button(
                                    rx.icon("heart", size=14),
                                    "В избранное",
                                    variant="outline",
                                    size="2",
                                    on_click=SearchState.add_to_favorites(partner["id"]),
                                ),
                                spacing="2",
                            ),
                            align="start",
                            width="100%",
                        ),
                        width="100%",
                        padding="1.5em",
                    ),
                    # Описание
                    rx.cond(
                        partner["description"],
                        rx.card(
                            rx.vstack(
                                rx.heading("О нас", size="4"),
                                rx.text(partner["description"], size="3"),
                                spacing="3",
                                width="100%",
                            ),
                            width="100%",
                            padding="1.5em",
                        ),
                    ),
                    # Услуги
                    rx.cond(
                        SearchState.partner_services,
                        rx.card(
                            rx.vstack(
                                rx.heading("Услуги", size="4"),
                                rx.separator(width="100%"),
                                rx.foreach(SearchState.partner_services, _service_row),
                                spacing="2",
                                width="100%",
                            ),
                            width="100%",
                            padding="1.5em",
                        ),
                    ),
                    # Отзывы
                    rx.card(
                        rx.vstack(
                            rx.heading("Отзывы", size="4"),
                            rx.cond(
                                SearchState.partner_reviews,
                                rx.vstack(
                                    rx.foreach(SearchState.partner_reviews, _review_card),
                                    spacing="3",
                                    width="100%",
                                ),
                                rx.text("Отзывов пока нет", size="3", color="gray"),
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        width="100%",
                        padding="1.5em",
                    ),
                    spacing="4",
                    width="100%",
                    padding_y="2em",
                ),
            ),
            max_width="900px",
        ),
    )


"""Страница избранных партнёров."""

import reflex as rx

from app.components.navbar import navbar
from app.components.partner_card import partner_card
from app.states.user import UserState


def favorites_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Избранное", size="7"),
                rx.cond(
                    UserState.favorites_loading,
                    rx.center(rx.spinner(size="3"), padding="3em"),
                    rx.cond(
                        UserState.favorites,
                        rx.vstack(
                            rx.foreach(UserState.favorites, partner_card),
                            spacing="4",
                            width="100%",
                        ),
                        rx.center(
                            rx.vstack(
                                rx.icon("heart", size=48, color="gray"),
                                rx.text("Список избранного пуст", size="4", color="gray"),
                                rx.text(
                                    "Добавляйте понравившихся мастеров с помощью ♡",
                                    size="3",
                                    color="gray",
                                    text_align="center",
                                ),
                                rx.link(
                                    rx.button("Найти партнёров", color_scheme="blue"),
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
            max_width="900px",
        ),
        on_mount=UserState.load_favorites,
    )


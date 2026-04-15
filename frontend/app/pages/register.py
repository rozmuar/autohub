"""Страница регистрации — редирект на /login (OTP поддерживает оба флоу)."""

import reflex as rx

from app.components.navbar import navbar
from app.states.auth import AuthState


def register() -> rx.Component:
    """Регистрация через OTP — та же страница, что и вход."""
    return rx.fragment(
        navbar(),
        rx.center(
            rx.card(
                rx.vstack(
                    rx.heading("Создать аккаунт", size="6", text_align="center"),
                    rx.text(
                        "Введите номер телефона — мы отправим код для регистрации",
                        size="3",
                        color="gray",
                        text_align="center",
                    ),
                    rx.input(
                        placeholder="+7 (999) 000-00-00",
                        value=AuthState.auth_phone,
                        on_change=AuthState.set_auth_phone,
                        type="tel",
                        size="3",
                        width="100%",
                    ),
                    rx.cond(
                        AuthState.auth_error != "",
                        rx.text(AuthState.auth_error, color="red", size="2"),
                    ),
                    rx.button(
                        "Продолжить",
                        on_click=AuthState.send_otp,
                        loading=AuthState.auth_loading,
                        color_scheme="blue",
                        size="3",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("Уже есть аккаунт?", size="2"),
                        rx.link("Войти", href="/login", size="2"),
                        justify="center",
                        spacing="2",
                    ),
                    spacing="4",
                    width="100%",
                ),
                max_width="420px",
                width="100%",
                padding="2em",
            ),
            min_height="90vh",
            padding="1em",
        ),
    )



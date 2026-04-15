"""Страница входа / регистрации  Aigocy Style."""

import reflex as rx

from app.components.navbar import navbar
from app.states.auth import AuthState


def _phone_step() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.i(class_name="bi bi-car-front-fill", style={"font-size": "2.5rem", "color": "var(--ag-red)"}),
            rx.el.span("AUTO", style={"font-weight": "900", "font-size": "1.4rem", "color": "var(--ag-dark)", "letter-spacing": "-.02em"}),
            rx.el.span("HUB", style={"font-weight": "900", "font-size": "1.4rem", "color": "var(--ag-red)", "letter-spacing": "-.02em"}),
            class_name="d-flex align-items-center gap-2 justify-content-center mb-4",
        ),
        rx.el.h4("Войти в Auto Hub", style={"font-weight": "800", "text-align": "center", "margin-bottom": ".4rem"}),
        rx.el.p("Введите номер телефона для входа или регистрации",
                style={"text-align": "center", "color": "var(--ag-gray)", "font-size": ".9rem", "margin-bottom": "1.5rem"}),
        rx.el.div(
            rx.el.label("Номер телефона", style={"font-size": ".85rem", "font-weight": "600", "margin-bottom": ".4rem", "display": "block"}),
            rx.el.input(
                placeholder="+7 (999) 000-00-00",
                value=AuthState.auth_phone,
                on_change=AuthState.set_auth_phone,
                type="tel",
                class_name="ag-form-control",
            ),
            class_name="ag-form-group",
        ),
        rx.cond(
            AuthState.auth_error != "",
            rx.el.div(
                rx.el.i(class_name="bi bi-exclamation-circle me-1"),
                AuthState.auth_error,
                class_name="ag-form-error",
            ),
        ),
        rx.el.button(
            rx.cond(AuthState.auth_loading,
                    rx.el.span(rx.el.span(class_name="spinner-border spinner-border-sm me-2"), "Отправляем"),
                    rx.el.span("Получить код")),
            on_click=AuthState.send_otp,
            class_name="ag-submit-btn",
            type="button",
        ),
        rx.el.div(
            rx.el.span("Нет аккаунта? ", style={"color": "var(--ag-gray)", "font-size": ".85rem"}),
            rx.el.a("Зарегистрироваться", href="/register",
                    style={"color": "var(--ag-red)", "font-size": ".85rem", "font-weight": "600", "text-decoration": "none"}),
            class_name="text-center mt-3",
        ),
    )


def _otp_step() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.i(class_name="bi bi-phone", style={"font-size": "2.5rem", "color": "var(--ag-red)"}),
            class_name="text-center mb-3",
        ),
        rx.el.h4("Введите код из SMS", style={"font-weight": "800", "text-align": "center", "margin-bottom": ".4rem"}),
        rx.el.p(
            rx.el.span("Код отправлен на "),
            rx.el.span(AuthState.auth_phone, style={"font-weight": "700", "color": "var(--ag-dark)"}),
            style={"text-align": "center", "color": "var(--ag-gray)", "font-size": ".9rem", "margin-bottom": "1.5rem"},
        ),
        rx.el.input(
            placeholder="000000",
            value=AuthState.auth_otp,
            on_change=AuthState.set_auth_otp,
            type="text",
            max_length=6,
            class_name="ag-form-control",
            style={"text-align": "center", "font-size": "2rem", "font-weight": "800",
                   "letter-spacing": ".4em", "padding": ".75rem"},
        ),
        rx.cond(
            AuthState.auth_error != "",
            rx.el.div(
                rx.el.i(class_name="bi bi-exclamation-circle me-1"),
                AuthState.auth_error,
                class_name="ag-form-error",
            ),
        ),
        rx.el.button(
            rx.cond(AuthState.auth_loading,
                    rx.el.span(rx.el.span(class_name="spinner-border spinner-border-sm me-2"), "Проверяем"),
                    rx.el.span("Подтвердить")),
            on_click=AuthState.verify_otp,
            class_name="ag-submit-btn",
            type="button",
        ),
        rx.el.button(
            rx.el.i(class_name="bi bi-arrow-left me-1"), "Изменить номер",
            on_click=AuthState.back_to_phone,
            class_name="ag-btn-outline w-100 mt-2",
            type="button",
        ),
    )


def _register_step() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.i(class_name="bi bi-person-plus", style={"font-size": "2.5rem", "color": "var(--ag-red)"}),
            class_name="text-center mb-3",
        ),
        rx.el.h4("Завершите регистрацию", style={"font-weight": "800", "text-align": "center", "margin-bottom": ".4rem"}),
        rx.el.p("Создаём аккаунт для вашего номера",
                style={"text-align": "center", "color": "var(--ag-gray)", "font-size": ".9rem", "margin-bottom": "1.5rem"}),
        rx.el.div(
            rx.el.label("Ваше имя", style={"font-size": ".85rem", "font-weight": "600", "margin-bottom": ".4rem", "display": "block"}),
            rx.el.input(placeholder="Иван", value=AuthState.auth_name,
                        on_change=AuthState.set_auth_name, class_name="ag-form-control"),
            class_name="ag-form-group",
        ),
        rx.el.div(
            rx.el.label("Email (необязательно)", style={"font-size": ".85rem", "font-weight": "600", "margin-bottom": ".4rem", "display": "block"}),
            rx.el.input(placeholder="ivan@example.com", value=AuthState.auth_email,
                        on_change=AuthState.set_auth_email, type="email", class_name="ag-form-control"),
            class_name="ag-form-group",
        ),
        rx.cond(
            AuthState.auth_error != "",
            rx.el.div(
                rx.el.i(class_name="bi bi-exclamation-circle me-1"),
                AuthState.auth_error,
                class_name="ag-form-error",
            ),
        ),
        rx.el.button(
            rx.cond(AuthState.auth_loading,
                    rx.el.span(rx.el.span(class_name="spinner-border spinner-border-sm me-2"), "Создаём"),
                    rx.el.span("Зарегистрироваться")),
            on_click=AuthState.complete_registration,
            class_name="ag-submit-btn",
            type="button",
        ),
    )


def login() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.div(
            rx.el.div(
                rx.match(
                    AuthState.auth_step,
                    ("phone", _phone_step()),
                    ("otp", _otp_step()),
                    ("register", _register_step()),
                    _phone_step(),
                ),
                class_name="ag-auth-card",
            ),
            class_name="ag-auth-page",
        ),
    )

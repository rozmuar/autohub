"""Navbar — dark automotive premium (AutoHub)."""

import reflex as rx

from app.state import AppState


def navbar() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            # Logo
            rx.el.a(
                "AUTO",
                rx.el.em("HUB"),
                href="/",
                class_name="ah-logo",
            ),
            # Desktop links
            rx.el.nav(
                rx.el.a("Главная", href="/", class_name="ah-nav-link"),
                rx.el.a("Поиск", href="/search", class_name="ah-nav-link"),
                rx.el.a("Новости", href="/news", class_name="ah-nav-link"),
                rx.el.a("Блог", href="/blog", class_name="ah-nav-link"),
                rx.el.a("О нас", href="/about", class_name="ah-nav-link"),
                class_name="ah-nav-links",
            ),
            # Auth area
            rx.el.div(
                rx.cond(
                    AppState.is_authenticated,
                    rx.el.div(
                        rx.el.a(
                            rx.el.i(class_name="bi bi-person-circle"),
                            AppState.display_name,
                            href="/profile",
                            class_name="ah-btn ah-btn-ghost",
                            style={"display": "inline-flex", "align-items": "center", "gap": ".4rem"},
                        ),
                        rx.el.a(
                            "Выйти",
                            href="#",
                            on_click=AppState.sign_out,
                            class_name="ah-btn ah-btn-outline",
                        ),
                        style={"display": "flex", "align-items": "center", "gap": ".75rem"},
                    ),
                    rx.el.div(
                        rx.el.a("Войти", href="/login", class_name="ah-btn ah-btn-ghost"),
                        rx.el.a("Записаться", href="/book", class_name="ah-btn ah-btn-primary"),
                        style={"display": "flex", "align-items": "center", "gap": ".75rem"},
                    ),
                ),
                class_name="ah-nav-cta",
            ),
            # Mobile hamburger
            rx.el.button(
                rx.el.span(),
                rx.el.span(),
                rx.el.span(),
                class_name="ah-hamburger d-lg-none",
                data_bs_toggle="offcanvas",
                data_bs_target="#ahMobileNav",
                aria_controls="ahMobileNav",
            ),
            class_name="ah-nav-inner container",
        ),
        # Mobile offcanvas
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    "AUTO",
                    rx.el.em("HUB"),
                    href="/",
                    class_name="ah-logo",
                ),
                rx.el.button(
                    rx.el.i(class_name="bi bi-x-lg"),
                    class_name="ah-offcanvas-close",
                    data_bs_dismiss="offcanvas",
                ),
                class_name="ah-offcanvas-header",
            ),
            rx.el.nav(
                rx.el.a("Главная", href="/", class_name="ah-offcanvas-link"),
                rx.el.a("Поиск", href="/search", class_name="ah-offcanvas-link"),
                rx.el.a("Новости", href="/news", class_name="ah-offcanvas-link"),
                rx.el.a("Блог", href="/blog", class_name="ah-offcanvas-link"),
                rx.el.a("О нас", href="/about", class_name="ah-offcanvas-link"),
                class_name="ah-offcanvas-nav",
            ),
            rx.el.div(
                rx.cond(
                    AppState.is_authenticated,
                    rx.el.div(
                        rx.el.a(
                            "Личный кабинет",
                            href="/profile",
                            class_name="ah-btn ah-btn-ghost",
                            style={"display": "block", "text-align": "center", "margin-bottom": ".75rem"},
                        ),
                        rx.el.a(
                            "Выйти",
                            href="#",
                            on_click=AppState.sign_out,
                            class_name="ah-btn ah-btn-outline",
                            style={"display": "block", "text-align": "center"},
                        ),
                    ),
                    rx.el.div(
                        rx.el.a(
                            "Войти",
                            href="/login",
                            class_name="ah-btn ah-btn-ghost",
                            style={"display": "block", "text-align": "center", "margin-bottom": ".75rem"},
                        ),
                        rx.el.a(
                            "Записаться",
                            href="/book",
                            class_name="ah-btn ah-btn-primary",
                            style={"display": "block", "text-align": "center"},
                        ),
                    ),
                ),
                class_name="ah-offcanvas-footer",
            ),
            id="ahMobileNav",
            class_name="ah-offcanvas offcanvas offcanvas-end",
            tab_index=-1,
        ),
        class_name="ah-nav",
    )

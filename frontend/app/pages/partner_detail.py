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


def _contact_row(icon: str, label: str, value: rx.Var, href_prefix: str = "") -> rx.Component:
    """Строка контакта — показывает значение."""
    return rx.hstack(
        rx.icon(icon, size=16, color="#6b7280"),
        rx.text(label, size="2", color="#6b7280", min_width="90px"),
        rx.cond(
            href_prefix != "",
            rx.link(value, href=href_prefix + value.to(str), size="2", color="#2563eb"),
            rx.text(value, size="2"),
        ),
        spacing="2",
        align="center",
        width="100%",
    )


def _contact_row_locked(icon: str, label: str) -> rx.Component:
    """Строка контакта — скрыта до подтверждения."""
    return rx.hstack(
        rx.icon(icon, size=16, color="#d1d5db"),
        rx.text(label, size="2", color="#d1d5db", min_width="90px"),
        rx.hstack(
            rx.icon("lock", size=12, color="#d1d5db"),
            rx.text("Доступно после верификации", size="2", color="#d1d5db"),
            spacing="1",
            align="center",
        ),
        spacing="2",
        align="center",
        width="100%",
    )


def _contacts_section(partner: rx.Var) -> rx.Component:
    is_active = partner["status"] == "active"
    return rx.card(
        rx.vstack(
            rx.heading("Контакты и информация", size="4"),
            rx.separator(width="100%"),
            # Телефон
            rx.cond(
                is_active,
                rx.cond(
                    partner["phone"],
                    _contact_row("phone", "Телефон", partner["phone"], "tel:"),
                    rx.fragment(),
                ),
                _contact_row_locked("phone", "Телефон"),
            ),
            # Email
            rx.cond(
                is_active,
                rx.cond(
                    partner["email"],
                    _contact_row("mail", "Email", partner["email"], "mailto:"),
                    rx.fragment(),
                ),
                _contact_row_locked("mail", "Email"),
            ),
            # Сайт
            rx.cond(
                is_active,
                rx.cond(
                    partner["website"],
                    _contact_row("globe", "Сайт", partner["website"]),
                    rx.fragment(),
                ),
                _contact_row_locked("globe", "Сайт"),
            ),
            # Время работы
            rx.cond(
                is_active,
                rx.cond(
                    partner["working_hours"],
                    _contact_row("clock", "Режим работы", partner["working_hours"]),
                    rx.fragment(),
                ),
                _contact_row_locked("clock", "Режим работы"),
            ),
            # Способы оплаты
            rx.cond(
                is_active,
                rx.cond(
                    partner["payment_methods"],
                    _contact_row("credit-card", "Оплата", partner["payment_methods"]),
                    rx.fragment(),
                ),
                _contact_row_locked("credit-card", "Оплата"),
            ),
            # Плашка "не подтверждён"
            rx.cond(
                ~is_active,
                rx.box(
                    rx.hstack(
                        rx.icon("info", size=14, color="#92400e"),
                        rx.text(
                            "Организация ещё не прошла верификацию. Контактные данные будут доступны после проверки.",
                            size="2",
                            color="#92400e",
                        ),
                        spacing="2",
                        align="start",
                    ),
                    background="#fef3c7",
                    border="1px solid #fcd34d",
                    border_radius="8px",
                    padding="0.75em 1em",
                    width="100%",
                    margin_top="0.5em",
                ),
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
        padding="1.5em",
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
                        rx.vstack(
                            # Верхняя строка: лого + название + кнопки
                            rx.hstack(
                                rx.cond(
                                    partner["logo_url"],
                                    rx.image(
                                        src=partner["logo_url"],
                                        width="80px",
                                        height="80px",
                                        border_radius="12px",
                                        object_fit="cover",
                                        flex_shrink="0",
                                    ),
                                    rx.box(
                                        rx.icon("wrench", size=36, color="#2563eb"),
                                        background="#eff6ff",
                                        border_radius="12px",
                                        padding="16px",
                                        flex_shrink="0",
                                    ),
                                ),
                                rx.vstack(
                                    rx.hstack(
                                        rx.heading(partner["name"], size="6"),
                                        rx.cond(
                                            partner["status"] == "active",
                                            rx.badge("Проверено", color_scheme="green", variant="soft"),
                                            rx.badge("На проверке", color_scheme="orange", variant="soft"),
                                        ),
                                        spacing="2",
                                        align="center",
                                        flex_wrap="wrap",
                                    ),
                                    rx.hstack(
                                        star_rating(partner["rating"]),
                                        rx.text(partner["rating"].to_string(), size="2", color="#374151"),
                                        rx.text(
                                            "(" + partner["reviews_count"].to(str) + " отзывов)",
                                            size="2",
                                            color="#9ca3af",
                                        ),
                                        spacing="2",
                                        align="center",
                                    ),
                                    rx.cond(
                                        partner["city"],
                                        rx.hstack(
                                            rx.icon("map-pin", size=14, color="#9ca3af"),
                                            rx.text(
                                                rx.cond(
                                                    partner["address"],
                                                    partner["city"].to(str) + ", " + partner["address"].to(str),
                                                    partner["city"].to(str),
                                                ),
                                                size="2",
                                                color="#6b7280",
                                            ),
                                            spacing="1",
                                            align="center",
                                        ),
                                        rx.cond(
                                            partner["address"],
                                            rx.hstack(
                                                rx.icon("map-pin", size=14, color="#9ca3af"),
                                                rx.text(partner["address"], size="2", color="#6b7280"),
                                                spacing="1",
                                                align="center",
                                            ),
                                        ),
                                    ),
                                    # Телефон в шапке — только если active
                                    rx.cond(
                                        partner["status"] == "active",
                                        rx.cond(
                                            partner["phone"],
                                            rx.link(
                                                rx.hstack(
                                                    rx.icon("phone", size=14, color="#2563eb"),
                                                    rx.text(partner["phone"], size="2", color="#2563eb", font_weight="500"),
                                                    spacing="1",
                                                    align="center",
                                                ),
                                                href="tel:" + partner["phone"].to(str),
                                            ),
                                        ),
                                    ),
                                    align_items="start",
                                    spacing="2",
                                    flex="1",
                                ),
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
                                    align_items="end",
                                    flex_shrink="0",
                                ),
                                align="start",
                                width="100%",
                                spacing="4",
                            ),
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
                                rx.text(partner["description"], size="3", line_height="1.7"),
                                spacing="3",
                                width="100%",
                            ),
                            width="100%",
                            padding="1.5em",
                        ),
                    ),
                    # Контакты
                    _contacts_section(partner),
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


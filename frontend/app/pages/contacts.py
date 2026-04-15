"""Страница контактов."""

import reflex as rx

from app.components.breadcrumbs import breadcrumbs
from app.components.navbar import navbar


def contacts_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                breadcrumbs([("Главная", "/"), ("Контакты", "/contacts")]),
                rx.heading("Контакты", size="7"),
                rx.text(
                    "Свяжитесь с нами любым удобным способом",
                    size="4",
                    color="gray",
                ),
                rx.grid(
                    # Общая информация
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("map-pin", size=24, color="blue"),
                                rx.heading("Адрес", size="5"),
                                spacing="2",
                                align="center",
                            ),
                            rx.text("г. Москва, ул. Автомобильная, д. 1", size="3"),
                            rx.text("ТЦ «АвтоПлаза», офис 205", size="3", color="gray"),
                            spacing="3",
                        ),
                        width="100%",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("phone", size=24, color="blue"),
                                rx.heading("Телефон", size="5"),
                                spacing="2",
                                align="center",
                            ),
                            rx.link(
                                rx.text("+7 (800) 123-45-67", size="4", weight="medium"),
                                href="tel:+78001234567",
                            ),
                            rx.text("Бесплатно по России", size="2", color="gray"),
                            rx.text("Пн–Пт: 09:00–20:00", size="2", color="gray"),
                            rx.text("Сб–Вс: 10:00–18:00", size="2", color="gray"),
                            spacing="3",
                        ),
                        width="100%",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("mail", size=24, color="blue"),
                                rx.heading("E-mail", size="5"),
                                spacing="2",
                                align="center",
                            ),
                            rx.link(
                                rx.text("support@autohub.ru", size="3"),
                                href="mailto:support@autohub.ru",
                            ),
                            rx.link(
                                rx.text("partners@autohub.ru", size="3"),
                                href="mailto:partners@autohub.ru",
                            ),
                            rx.text("Ответ в течение 24 часов", size="2", color="gray"),
                            spacing="3",
                        ),
                        width="100%",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("message-circle", size=24, color="blue"),
                                rx.heading("Мессенджеры", size="5"),
                                spacing="2",
                                align="center",
                            ),
                            rx.hstack(
                                rx.icon("send", size=16, color="blue"),
                                rx.link("Telegram", href="https://t.me/autohub", is_external=True, size="3"),
                                spacing="2",
                                align="center",
                            ),
                            rx.hstack(
                                rx.icon("message-square", size=16, color="green"),
                                rx.link("WhatsApp", href="https://wa.me/78001234567", is_external=True, size="3"),
                                spacing="2",
                                align="center",
                            ),
                            spacing="3",
                        ),
                        width="100%",
                    ),
                    columns=rx.breakpoints(initial="1", sm="2"),
                    gap="4",
                    width="100%",
                ),
                # Форма обратной связи
                rx.card(
                    rx.vstack(
                        rx.heading("Написать нам", size="5"),
                        rx.text("Оставьте заявку и мы свяжемся с вами", size="2", color="gray"),
                        rx.grid(
                            rx.vstack(
                                rx.text("Имя", size="2", weight="medium"),
                                rx.input(placeholder="Ваше имя", size="3", width="100%"),
                                spacing="1",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.text("E-mail", size="2", weight="medium"),
                                rx.input(placeholder="email@example.com", type="email", size="3", width="100%"),
                                spacing="1",
                                width="100%",
                            ),
                            columns="2",
                            gap="4",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Сообщение", size="2", weight="medium"),
                            rx.text_area(
                                placeholder="Опишите ваш вопрос...",
                                rows="5",
                                width="100%",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        rx.button(
                            "Отправить сообщение",
                            size="3",
                            color_scheme="blue",
                        ),
                        spacing="4",
                        width="100%",
                        align="start",
                    ),
                    width="100%",
                ),
                spacing="6",
                width="100%",
            ),
            max_width="1000px",
            py="8",
        ),
    )


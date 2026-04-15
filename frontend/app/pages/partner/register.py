"""Регистрация партнёра — мастер в 3 шага."""

import reflex as rx

from app.components.navbar import navbar
from app.states.partner import PartnerState


def _step_indicator(current: rx.Var) -> rx.Component:
    def _dot(n: int) -> rx.Component:
        return rx.box(
            rx.text(str(n), size="1", color=rx.cond(current >= n, "white", "gray")),
            background=rx.cond(current >= n, "#2563eb", "#e5e7eb"),
            border_radius="50%",
            width="28px",
            height="28px",
            display="flex",
            align_items="center",
            justify_content="center",
        )

    return rx.hstack(
        _dot(1),
        rx.box(height="2px", background="#e5e7eb", flex="1"),
        _dot(2),
        rx.box(height="2px", background="#e5e7eb", flex="1"),
        _dot(3),
        align="center",
        width="100%",
    )


def _step1() -> rx.Component:
    return rx.vstack(
        rx.heading("Шаг 1: Основная информация", size="4"),
        rx.vstack(
            rx.text("Название компании / ИМЯ мастера", size="2", color="gray"),
            rx.input(
                placeholder="ООО Автосервис или Иванов Иван",
                value=PartnerState.reg_company_name,
                on_change=PartnerState.set_reg_company_name,
                size="2",
                width="100%",
            ),
            spacing="1",
            width="100%",
        ),
        rx.vstack(
            rx.text("Тип партнёра", size="2", color="gray"),
            rx.select.root(
                rx.select.trigger(placeholder="Выберите тип"),
                rx.select.content(
                    rx.select.item("Физическое лицо", value="individual"),
                    rx.select.item("Самозанятый", value="self_employed"),
                    rx.select.item("ИП / ООО", value="legal"),
                ),
                value=PartnerState.reg_partner_type,
                on_change=PartnerState.set_reg_partner_type,
                size="2",
            ),
            spacing="1",
            width="100%",
        ),
        rx.vstack(
            rx.text("ИНН", size="2", color="gray"),
            rx.input(
                placeholder="123456789012",
                value=PartnerState.reg_inn,
                on_change=PartnerState.set_reg_inn,
                size="2",
                width="100%",
            ),
            spacing="1",
            width="100%",
        ),
        rx.vstack(
            rx.text("Описание (необязательно)", size="2", color="gray"),
            rx.text_area(
                placeholder="Расскажите о своих услугах...",
                value=PartnerState.reg_description,
                on_change=PartnerState.set_reg_description,
                rows="3",
                width="100%",
            ),
            spacing="1",
            width="100%",
        ),
        rx.button(
            "Далее →",
            on_click=PartnerState.reg_next,
            color_scheme="blue",
            size="3",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def _step2() -> rx.Component:
    return rx.vstack(
        rx.heading("Шаг 2: Адрес и контакты", size="4"),
        rx.vstack(
            rx.text("Адрес", size="2", color="gray"),
            rx.input(
                placeholder="г. Москва, ул. Ленина, д. 1",
                value=PartnerState.reg_address,
                on_change=PartnerState.set_reg_address,
                size="2",
                width="100%",
            ),
            spacing="1",
            width="100%",
        ),
        rx.vstack(
            rx.text("Город", size="2", color="gray"),
            rx.input(
                placeholder="Москва",
                value=PartnerState.reg_city,
                on_change=PartnerState.set_reg_city,
                size="2",
                width="100%",
            ),
            spacing="1",
            width="100%",
        ),
        rx.vstack(
            rx.text("Телефон для клиентов (необязательно)", size="2", color="gray"),
            rx.input(
                placeholder="+7 (999) 000-00-00",
                value=PartnerState.reg_phone,
                on_change=PartnerState.set_reg_phone,
                type="tel",
                size="2",
                width="100%",
            ),
            spacing="1",
            width="100%",
        ),
        rx.hstack(
            rx.button(
                "← Назад",
                variant="outline",
                size="3",
                on_click=PartnerState.set_reg_step(1),
            ),
            rx.button(
                "Далее →",
                on_click=PartnerState.reg_next,
                color_scheme="blue",
                size="3",
                flex="1",
            ),
            spacing="3",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def _step3() -> rx.Component:
    return rx.vstack(
        rx.heading("Шаг 3: Подтверждение", size="4"),
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text("Компания:", size="2", color="gray"),
                    rx.text(PartnerState.reg_company_name, size="2", font_weight="600"),
                    justify="between",
                    width="100%",
                ),
                rx.hstack(
                    rx.text("Тип:", size="2", color="gray"),
                    rx.text(PartnerState.reg_partner_type, size="2"),
                    justify="between",
                    width="100%",
                ),
                rx.hstack(
                    rx.text("ИНН:", size="2", color="gray"),
                    rx.text(PartnerState.reg_inn, size="2"),
                    justify="between",
                    width="100%",
                ),
                rx.hstack(
                    rx.text("Адрес:", size="2", color="gray"),
                    rx.text(PartnerState.reg_address, size="2"),
                    justify="between",
                    width="100%",
                ),
                spacing="2",
                width="100%",
            ),
            width="100%",
            background="#f8fafc",
        ),
        rx.cond(
            PartnerState.reg_error != "",
            rx.text(PartnerState.reg_error, color="red", size="2"),
        ),
        rx.hstack(
            rx.button(
                "← Назад",
                variant="outline",
                size="3",
                on_click=PartnerState.set_reg_step(2),
            ),
            rx.button(
                "Зарегистрироваться партнёром",
                on_click=PartnerState.submit_registration,
                loading=PartnerState.reg_loading,
                color_scheme="blue",
                size="3",
                flex="1",
            ),
            spacing="3",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def partner_register_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.container(
            rx.center(
                rx.vstack(
                    # Баннер бесплатного размещения
                    rx.box(
                        rx.hstack(
                            rx.icon("circle-check", color="#22c55e", size=22),
                            rx.vstack(
                                rx.text("Размещение бесплатно", font_weight="700", size="3"),
                                rx.text(
                                    "В будущем появятся платные тарифы с расширенными возможностями. "
                                    "Сейчас можно зарегистрироваться бесплатно навсегда.",
                                    size="2", color="gray",
                                ),
                                spacing="1",
                                align="start",
                            ),
                            align="start",
                            spacing="3",
                        ),
                        background="#f0fdf4",
                        border="1px solid #bbf7d0",
                        border_radius="8px",
                        padding="1em",
                        width="100%",
                        max_width="540px",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.heading("Стать партнёром Auto Hub", size="6", text_align="center"),
                            rx.text(
                                "Предлагайте услуги тысячам автовладельцев",
                                size="3",
                                color="gray",
                                text_align="center",
                            ),
                            _step_indicator(PartnerState.reg_step),
                            rx.match(
                                PartnerState.reg_step,
                                (1, _step1()),
                                (2, _step2()),
                                (3, _step3()),
                                _step1(),
                            ),
                            spacing="5",
                            width="100%",
                        ),
                        max_width="540px",
                        width="100%",
                        padding="2em",
                    ),
                    spacing="3",
                    width="100%",
                    align="center",
                ),
                padding="2em",
            ),
        ),
    )



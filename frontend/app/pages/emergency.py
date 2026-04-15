"""Страница экстренной помощи — Phase 2."""

import reflex as rx

from app.components.navbar import navbar
from app.states.emergency import EmergencyState


_TYPES = [
    ("tow_truck", "Эвакуатор", "truck"),
    ("jump_start", "Прикурить", "zap"),
    ("fuel", "Топливо", "fuel"),
    ("tire", "Шиномонтаж", "circle"),
    ("stuck", "Застрял", "anchor"),
    ("other", "Другое", "help-circle"),
]


def _type_card(type_id: str, label: str, icon: str) -> rx.Component:
    is_selected = EmergencyState.em_type == type_id
    return rx.card(
        rx.vstack(
            rx.icon(icon, size=28, color=rx.cond(is_selected, "white", "blue")),
            rx.text(label, size="2", font_weight="500", color=rx.cond(is_selected, "white", "inherit")),
            spacing="2",
            align="center",
        ),
        background=rx.cond(is_selected, "#2563eb", "white"),
        border=rx.cond(is_selected, "2px solid #2563eb", "1px solid #e5e7eb"),
        cursor="pointer",
        on_click=EmergencyState.select_type(type_id),
        padding="1.5em",
        _hover={"border": "2px solid #2563eb"},
    )


def _step_type() -> rx.Component:
    return rx.vstack(
        rx.heading("Нужна помощь?", size="6", text_align="center"),
        rx.text(
            "Выберите тип необходимой помощи",
            size="3",
            color="gray",
            text_align="center",
        ),
        rx.grid(
            _type_card("tow_truck", "Эвакуатор", "truck"),
            _type_card("jump_start", "Прикурить", "zap"),
            _type_card("fuel", "Топливо", "fuel"),
            _type_card("tire", "Шиномонтаж", "circle"),
            _type_card("stuck", "Застрял", "anchor"),
            _type_card("other", "Другое", "circle-help"),
            columns="3",
            spacing="3",
            width="100%",
        ),
        rx.text_area(
            placeholder="Описание ситуации (необязательно)...",
            value=EmergencyState.em_description,
            on_change=EmergencyState.set_em_description,
            rows="3",
            width="100%",
        ),
        rx.input(
            placeholder="Адрес или описание местоположения",
            value=EmergencyState.em_address,
            on_change=EmergencyState.set_em_address,
            size="3",
            width="100%",
        ),
        rx.cond(
            EmergencyState.em_error,
            rx.text(EmergencyState.em_error, color="red", size="2"),
        ),
        rx.button(
            rx.icon("siren", size=18),
            "Вызвать помощь",
            on_click=EmergencyState.create_request,
            loading=EmergencyState.em_loading,
            color_scheme="red",
            size="3",
            width="100%",
            disabled=EmergencyState.em_type == "",
        ),
        spacing="4",
        width="100%",
    )


def _step_searching() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.spinner(size="3", color="blue"),
            rx.heading("Ищем ближайших мастеров...", size="5", text_align="center"),
            rx.text(
                "Обычно это занимает 1-3 минуты",
                size="3",
                color="gray",
                text_align="center",
            ),
            rx.text(
                "Заявка #", EmergencyState.em_request_id,
                size="2",
                color="gray",
            ),
            rx.hstack(
                rx.button(
                    "Обновить статус",
                    on_click=EmergencyState.poll_status,
                    variant="outline",
                    size="2",
                ),
                rx.button(
                    "Отменить заявку",
                    on_click=EmergencyState.cancel_request,
                    color_scheme="red",
                    variant="ghost",
                    size="2",
                ),
                spacing="3",
            ),
            spacing="5",
            align="center",
        ),
        padding="4em",
        width="100%",
    )


def _step_found() -> rx.Component:
    responses = EmergencyState.em_responses
    return rx.vstack(
        rx.hstack(
            rx.icon("circle-check", size=28, color="green"),
            rx.heading("Мастер найден!", size="5"),
            spacing="3",
            align="center",
        ),
        rx.cond(
            responses,
            rx.vstack(
                rx.foreach(
                    responses,
                    lambda r: rx.card(
                        rx.hstack(
                            rx.vstack(
                                rx.text(r["partner_name"], font_weight="600", size="3"),
                                rx.text(
                                    "Прибудет через: ", r["eta_minutes"].to_string(), " мин",
                                    size="2",
                                    color="gray",
                                ),
                                rx.text(
                                    "Стоимость: ", r["price"].to_string(), " ₽",
                                    size="3",
                                    font_weight="500",
                                ),
                                spacing="1",
                                align_items="start",
                            ),
                            rx.spacer(),
                            rx.button(
                                "Принять",
                                color_scheme="green",
                                size="2",
                            ),
                            align="center",
                            width="100%",
                        ),
                        width="100%",
                    ),
                ),
                spacing="2",
                width="100%",
            ),
        ),
        rx.button(
            "Сбросить и начать снова",
            on_click=EmergencyState.em_reset,
            variant="ghost",
            size="2",
        ),
        spacing="4",
        width="100%",
    )


def _step_inprogress() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.icon("wrench", size=48, color="blue"),
            rx.heading("Работа в процессе", size="5"),
            rx.text(
                "Мастер прибыл и выполняет работу",
                size="3",
                color="gray",
            ),
            rx.button(
                "Обновить статус",
                on_click=EmergencyState.poll_status,
                size="2",
            ),
            spacing="4",
            align="center",
        ),
        padding="4em",
    )


def emergency_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.container(
            rx.vstack(
                # Шапка SOS
                rx.box(
                    rx.hstack(
                        rx.icon("siren", size=28, color="white"),
                        rx.heading("Экстренная помощь", size="6", color="white"),
                        spacing="3",
                        align="center",
                    ),
                    background="linear-gradient(135deg, #dc2626, #991b1b)",
                    border_radius="12px",
                    padding="1.5em",
                    width="100%",
                ),
                rx.card(
                    rx.match(
                        EmergencyState.em_step,
                        ("type", _step_type()),
                        ("confirm", _step_type()),
                        ("searching", _step_searching()),
                        ("found", _step_found()),
                        ("inprogress", _step_inprogress()),
                        _step_type(),
                    ),
                    width="100%",
                    padding="2em",
                ),
                spacing="4",
                padding_y="2em",
                width="100%",
            ),
            max_width="600px",
        ),
    )


"""Страница бронирования слота."""

import reflex as rx

from app.components.navbar import navbar
from app.states.booking import BookingState
from app.state import AppState


def _slot_btn(slot: rx.Var) -> rx.Component:
    is_selected = BookingState.selected_slot_id == slot["id"].to_string()
    return rx.button(
        rx.vstack(
            rx.text(slot["start_time"], size="2", font_weight="500"),
            rx.cond(
                slot["service_name"],
                rx.text(slot["service_name"], size="1", color="gray"),
            ),
            spacing="0",
            align="center",
        ),
        variant=rx.cond(is_selected, "solid", "outline"),
        color_scheme=rx.cond(is_selected, "blue", "gray"),
        on_click=BookingState.select_slot(slot["id"].to_string()),
        size="2",
        disabled=~slot["is_available"],
    )


def booking_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.container(
            rx.vstack(
                rx.heading("Записаться", size="7"),
                rx.cond(
                    BookingState.booking_success,
                    # Успешное бронирование
                    rx.card(
                        rx.center(
                            rx.vstack(
                                rx.icon("circle-check", size=56, color="green"),
                                rx.heading("Запись оформлена!", size="5"),
                                rx.text(
                                    rx.text("Номер брони: ", BookingState.created_booking_id),
                                    size="3",
                                    color="gray",
                                ),
                                rx.hstack(
                                    rx.link(
                                        rx.button("Мои заказы", color_scheme="blue", size="3"),
                                        href="/orders",
                                    ),
                                    rx.link(
                                        rx.button("На главную", variant="outline", size="3"),
                                        href="/",
                                    ),
                                    spacing="3",
                                ),
                                spacing="4",
                                align="center",
                            ),
                        ),
                        padding="3em",
                        width="100%",
                    ),
                    # Форма бронирования
                    rx.vstack(
                        # Выбор даты
                        rx.card(
                            rx.vstack(
                                rx.heading("Период", size="4"),
                                rx.hstack(
                                    rx.vstack(
                                        rx.text("С", size="2", color="gray"),
                                        rx.input(
                                            type="date",
                                            value=BookingState.date_from,
                                            on_change=BookingState.set_date_from,
                                            size="2",
                                        ),
                                        spacing="1",
                                    ),
                                    rx.vstack(
                                        rx.text("По", size="2", color="gray"),
                                        rx.input(
                                            type="date",
                                            value=BookingState.date_to,
                                            on_change=BookingState.set_date_to,
                                            size="2",
                                        ),
                                        spacing="1",
                                    ),
                                    rx.button(
                                        "Показать слоты",
                                        on_click=BookingState.load_slots,
                                        loading=BookingState.slots_loading,
                                        size="2",
                                        align_self="end",
                                    ),
                                    spacing="3",
                                    align="end",
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            padding="1.5em",
                            width="100%",
                        ),
                        # Слоты
                        rx.cond(
                            BookingState.slots_loading,
                            rx.center(rx.spinner(size="3"), padding="2em"),
                            rx.cond(
                                BookingState.available_slots,
                                rx.card(
                                    rx.vstack(
                                        rx.heading("Доступные слоты", size="4"),
                                        rx.flex(
                                            rx.foreach(BookingState.available_slots, _slot_btn),
                                            wrap="wrap",
                                            gap="2",
                                        ),
                                        spacing="3",
                                        width="100%",
                                    ),
                                    padding="1.5em",
                                    width="100%",
                                ),
                                rx.text(
                                    "Выберите период для отображения слотов",
                                    size="3",
                                    color="gray",
                                ),
                            ),
                        ),
                        # Автомобиль (опционально)
                        rx.card(
                            rx.vstack(
                                rx.heading("Автомобиль (необязательно)", size="4"),
                                rx.select.root(
                                    rx.select.trigger(placeholder="Выберите из гаража"),
                                    rx.select.content(
                                        rx.foreach(
                                            BookingState.user_vehicles,
                                            lambda v: rx.select.item(
                                                rx.text(v["brand"], " ", v["model"]),
                                                value=v["id"].to_string(),
                                            ),
                                        ),
                                    ),
                                    value=BookingState.vehicle_id,
                                    on_change=BookingState.set_vehicle_id,
                                    size="2",
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            padding="1.5em",
                            width="100%",
                        ),
                        # Кнопка записи
                        rx.cond(
                            BookingState.booking_error != "",
                            rx.text(BookingState.booking_error, color="red", size="2"),
                        ),
                        rx.button(
                            "Подтвердить запись",
                            on_click=BookingState.create_booking,
                            loading=BookingState.booking_loading,
                            disabled=BookingState.selected_slot_id == "",
                            color_scheme="blue",
                            size="3",
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                ),
                spacing="5",
                padding_y="2em",
                width="100%",
            ),
            max_width="700px",
        ),
        on_mount=BookingState.load_user_vehicles,
    )


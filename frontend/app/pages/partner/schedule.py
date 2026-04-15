"""Расписание работы партнёра."""

import reflex as rx

from app.components.navbar import navbar
from app.states.partner import PartnerState


_DAYS = [
    ("monday", "Понедельник"),
    ("tuesday", "Вторник"),
    ("wednesday", "Среда"),
    ("thursday", "Четверг"),
    ("friday", "Пятница"),
    ("saturday", "Суббота"),
    ("sunday", "Воскресенье"),
]


def partner_schedule_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.container(
            rx.vstack(
                rx.hstack(
                    rx.heading("Расписание работы", size="7"),
                    rx.spacer(),
                    rx.button(
                        "Сохранить",
                        color_scheme="blue",
                        size="2",
                        on_click=PartnerState.save_schedule,
                    ),
                    align="center",
                    width="100%",
                ),
                rx.card(
                    rx.vstack(
                        rx.foreach(
                            PartnerState.schedule,
                            lambda day: rx.hstack(
                                rx.switch(
                                    checked=day["is_working"],
                                    on_change=PartnerState.toggle_day(day["day_of_week"]),
                                ),
                                rx.text(day["day_label"], size="3", min_width="120px"),
                                rx.cond(
                                    day["is_working"],
                                    rx.hstack(
                                        rx.input(
                                            type="time",
                                            value=day["open_time"],
                                            size="2",
                                        ),
                                        rx.text("—", size="2"),
                                        rx.input(
                                            type="time",
                                            value=day["close_time"],
                                            size="2",
                                        ),
                                        spacing="2",
                                        align="center",
                                    ),
                                    rx.text("Выходной", size="2", color="gray"),
                                ),
                                align="center",
                                spacing="4",
                                padding_y="0.75em",
                                width="100%",
                            ),
                        ),
                        spacing="0",
                        divide_y="1px solid #e5e7eb",
                        width="100%",
                    ),
                    padding="1.5em",
                    width="100%",
                ),
                # Длина слота
                rx.card(
                    rx.hstack(
                        rx.vstack(
                            rx.text("Длина слота", size="2", color="gray"),
                            rx.text(
                                "Минимальное время одной записи",
                                size="2",
                                color="gray",
                            ),
                            spacing="1",
                            align_items="start",
                        ),
                        rx.spacer(),
                        rx.select.root(
                            rx.select.trigger(),
                            rx.select.content(
                                rx.select.item("30 минут", value="30"),
                                rx.select.item("60 минут", value="60"),
                                rx.select.item("90 минут", value="90"),
                                rx.select.item("120 минут", value="120"),
                            ),
                            default_value="60",
                            size="2",
                        ),
                        align="center",
                        width="100%",
                    ),
                    padding="1.5em",
                    width="100%",
                ),
                spacing="5",
                padding_y="2em",
                width="100%",
            ),
            max_width="700px",
        ),
        on_mount=PartnerState.load_schedule,
    )


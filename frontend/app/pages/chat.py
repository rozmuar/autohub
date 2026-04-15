"""Страница чата — Phase 2."""

import reflex as rx

from app.components.navbar import navbar
from app.states.chat import ChatState
from app.state import AppState


def _room_item(room: rx.Var) -> rx.Component:
    is_active = ChatState.active_room_id == room["id"].to_string()
    return rx.hstack(
        rx.cond(
            room["partner_logo"],
            rx.image(
                src=room["partner_logo"],
                width="40px",
                height="40px",
                border_radius="50%",
                object_fit="cover",
            ),
            rx.box(
                rx.icon("user-circle", size=24, color="blue"),
                background="#eff6ff",
                border_radius="50%",
                padding="8px",
            ),
        ),
        rx.vstack(
            rx.text(
                rx.cond(
                    room["partner_name"],
                    room["partner_name"],
                    "Чат",
                ),
                font_weight=rx.cond(room["unread_count"], "700", "500"),
                size="3",
            ),
            rx.text(
                rx.cond(room["last_message"], room["last_message"], ""),
                size="2",
                color="gray",
                overflow="hidden",
                text_overflow="ellipsis",
                white_space="nowrap",
                max_width="160px",
            ),
            spacing="0",
            align_items="start",
        ),
        rx.spacer(),
        rx.cond(
            room["unread_count"],
            rx.badge(
                room["unread_count"],
                color_scheme="blue",
                variant="solid",
                size="1",
            ),
        ),
        background=rx.cond(is_active, "#eff6ff", "transparent"),
        padding="0.75em",
        border_radius="8px",
        cursor="pointer",
        on_click=ChatState.open_room(room["id"].to_string()),
        width="100%",
        align="center",
        _hover={"background": "#f8fafc"},
    )


def _message_bubble(msg: rx.Var) -> rx.Component:
    is_mine = msg["sender_id"].to_string() == AppState.user_id
    return rx.hstack(
        rx.cond(~is_mine, rx.spacer()),
        rx.box(
            rx.vstack(
                rx.text(msg["content"], size="2"),
                rx.text(
                    msg["created_at"],
                    size="1",
                    color=rx.cond(is_mine, "#bfdbfe", "gray"),
                    align_self="end",
                ),
                spacing="1",
                align_items=rx.cond(is_mine, "end", "start"),
            ),
            background=rx.cond(is_mine, "#2563eb", "#f1f5f9"),
            color=rx.cond(is_mine, "white", "inherit"),
            border_radius=rx.cond(is_mine, "12px 12px 2px 12px", "12px 12px 12px 2px"),
            padding="0.75em 1em",
            max_width="70%",
        ),
        rx.cond(is_mine, rx.spacer()),
        width="100%",
    )


def chat_page() -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.box(
            rx.hstack(
                # Левая панель — список комнат
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Сообщения", size="4"),
                            rx.spacer(),
                            rx.button(
                                rx.icon("refresh-cw", size=14),
                                variant="ghost",
                                size="1",
                                on_click=ChatState.load_rooms,
                            ),
                            align="center",
                            width="100%",
                        ),
                        rx.cond(
                            ChatState.rooms_loading,
                            rx.center(rx.spinner(size="2"), padding="1em"),
                            rx.cond(
                                ChatState.rooms,
                                rx.vstack(
                                    rx.foreach(ChatState.rooms, _room_item),
                                    spacing="1",
                                    width="100%",
                                    overflow_y="auto",
                                ),
                                rx.center(
                                    rx.vstack(
                                        rx.icon("message-square", size=32, color="gray"),
                                        rx.text("Нет диалогов", size="3", color="gray"),
                                        spacing="2",
                                        align="center",
                                    ),
                                    padding="2em",
                                ),
                            ),
                        ),
                        spacing="3",
                        padding="1em",
                        height="100%",
                    ),
                    width="280px",
                    min_width="280px",
                    border_right="1px solid #e5e7eb",
                    height="calc(100vh - 64px)",
                    overflow_y="auto",
                ),
                # Правая панель — сообщения
                rx.cond(
                    ChatState.active_room_id != "",
                    rx.vstack(
                        # Шапка чата
                        rx.hstack(
                            rx.icon("message-circle", size=20, color="blue"),
                            rx.text("Чат", font_weight="600", size="3"),
                            rx.spacer(),
                            rx.button(
                                rx.icon("refresh-cw", size=14),
                                variant="ghost",
                                size="1",
                                on_click=ChatState.load_messages,
                            ),
                            align="center",
                            padding="0.75em 1em",
                            border_bottom="1px solid #e5e7eb",
                            width="100%",
                        ),
                        # Сообщения
                        rx.box(
                            rx.cond(
                                ChatState.messages_loading,
                                rx.center(rx.spinner(size="2"), padding="2em"),
                                rx.cond(
                                    ChatState.messages,
                                    rx.vstack(
                                        rx.foreach(ChatState.messages, _message_bubble),
                                        spacing="2",
                                        padding="1em",
                                        width="100%",
                                        align_items="stretch",
                                    ),
                                    rx.center(
                                        rx.text("Нет сообщений. Начните переписку!", size="3", color="gray"),
                                        padding="3em",
                                    ),
                                ),
                            ),
                            flex="1",
                            overflow_y="auto",
                            width="100%",
                        ),
                        # Ввод сообщения
                        rx.hstack(
                            rx.input(
                                placeholder="Напишите сообщение...",
                                value=ChatState.new_message,
                                on_change=ChatState.set_new_message,
                                on_key_down=rx.cond(
                                    rx.Var.create("event.key === 'Enter'"),
                                    ChatState.send_message,
                                    rx.noop(),
                                ),
                                size="2",
                                flex="1",
                            ),
                            rx.button(
                                rx.icon("send", size=16),
                                on_click=ChatState.send_message,
                                loading=ChatState.send_loading,
                                color_scheme="blue",
                                size="2",
                                disabled=ChatState.new_message == "",
                            ),
                            padding="0.75em 1em",
                            border_top="1px solid #e5e7eb",
                            width="100%",
                            spacing="2",
                        ),
                        height="calc(100vh - 64px)",
                        flex="1",
                        overflow="hidden",
                    ),
                    rx.center(
                        rx.vstack(
                            rx.icon("message-square-dashed", size=48, color="gray"),
                            rx.text("Выберите диалог", size="4", color="gray"),
                            spacing="3",
                            align="center",
                        ),
                        flex="1",
                    ),
                ),
                spacing="0",
                height="calc(100vh - 64px)",
                width="100%",
                overflow="hidden",
            ),
            width="100%",
        ),
        on_mount=ChatState.load_rooms,
    )


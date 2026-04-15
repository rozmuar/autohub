"""Компонент звёздного рейтинга."""

import reflex as rx


def star_rating(rating: rx.Var, size: int = 16) -> rx.Component:
    """Отображает рейтинг в виде звёзд (read-only)."""
    def _star(n: int) -> rx.Component:
        return rx.icon(
            "star",
            size=size,
            color=rx.cond(rating.to(int) >= n, "#f59e0b", "#d1d5db"),
            fill=rx.cond(rating.to(int) >= n, "#f59e0b", "none"),
        )

    return rx.hstack(
        _star(1), _star(2), _star(3), _star(4), _star(5),
        spacing="1",
        display="inline-flex",
        align="center",
    )


def star_rating_input(current: rx.Var, on_change) -> rx.Component:
    """Интерактивный выбор рейтинга."""
    def _btn(n: int) -> rx.Component:
        return rx.icon(
            "star",
            size=24,
            color=rx.cond(current.to(int) >= n, "#f59e0b", "#d1d5db"),
            fill=rx.cond(current.to(int) >= n, "#f59e0b", "none"),
            cursor="pointer",
            on_click=lambda: on_change(n),
            _hover={"color": "#f59e0b", "fill": "#f59e0b"},
        )

    return rx.hstack(
        _btn(1), _btn(2), _btn(3), _btn(4), _btn(5),
        spacing="1",
        display="inline-flex",
    )

    return rx.hstack(
        _btn(1), _btn(2), _btn(3), _btn(4), _btn(5),
        spacing="1",
        display="inline-flex",
    )

    return rx.hstack(
        _btn(1), _btn(2), _btn(3), _btn(4), _btn(5),
        spacing="1",
        display="inline-flex",
    )


"""Компонент хлебных крошек."""

import reflex as rx


def breadcrumbs(crumbs: list[tuple[str, str]]) -> rx.Component:
    """Хлебные крошки.

    Args:
        crumbs: список (label, href), последний элемент — текущая страница.
    """
    items: list[rx.Component] = []
    for i, (label, href) in enumerate(crumbs):
        is_last = i == len(crumbs) - 1
        if is_last:
            items.append(
                rx.text(label, size="2", color="gray", weight="medium")
            )
        else:
            items.append(
                rx.link(label, href=href, size="2", color="blue")
            )
            items.append(
                rx.text("/", size="2", color="gray", mx="1")
            )
    return rx.hstack(
        *items,
        spacing="1",
        align="center",
        py="2",
        wrap="wrap",
    )


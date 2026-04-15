"""Страница детали акции  Aigocy Style."""

import reflex as rx

from app.components.navbar import navbar
from app.pages.index import _footer
from app.states.content import ContentState


def promo_detail_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    rx.el.a("Главная", href="/"), " / ",
                    rx.el.a("Акции", href="/promos"), " / ",
                    ContentState.art_title,
                    class_name="ag-breadcrumb",
                ),
                class_name="mb-2",
            ),
            rx.el.h1(ContentState.art_title),
            class_name="ag-page-header",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    # Основной контент
                    rx.el.div(
                        rx.cond(
                            ContentState.article_loading,
                            rx.el.div(rx.el.div(class_name="spinner-border text-secondary"), class_name="text-center py-5"),
                            rx.el.div(
                                # Обложка
                                rx.cond(
                                    ContentState.art_cover_url,
                                    rx.el.img(src=ContentState.art_cover_url, alt=ContentState.art_title,
                                              class_name="ag-article-cover"),
                                ),
                                # Мета: скидка + срок
                                rx.el.div(
                                    rx.cond(
                                        ContentState.art_discount > 0,
                                        rx.el.span(
                                            "Скидка ", ContentState.art_discount, "%",
                                            style={"background": "var(--ag-red)", "color": "white",
                                                   "padding": ".35rem .9rem", "border-radius": "50px",
                                                   "font-weight": "800", "font-size": ".9rem"},
                                        ),
                                    ),
                                    rx.cond(
                                        ContentState.art_promo_until,
                                        rx.el.span(
                                            rx.el.i(class_name="bi bi-calendar3 me-1"),
                                            "Действует до: ", ContentState.art_promo_until,
                                            style={"font-size": ".85rem", "color": "var(--ag-gray)"},
                                        ),
                                    ),
                                    class_name="d-flex gap-3 mb-4 flex-wrap align-items-center",
                                ),
                                # Контент
                                rx.el.div(
                                    rx.el.p(ContentState.art_body),
                                    class_name="ag-article",
                                ),
                                # CTA акции
                                rx.el.div(
                                    rx.el.a("Записаться со скидкой", href="/search",
                                            class_name="ag-btn-red mt-4 d-inline-block"),
                                    class_name="mt-3",
                                ),
                            ),
                        ),
                        class_name="col-lg-8",
                    ),
                    # Сайдбар
                    rx.el.div(
                        rx.el.aside(
                            rx.el.div(
                                rx.el.div("Другие акции", class_name="ag-sidebar-widget-title"),
                                rx.el.a("Перейти ко всем акциям ", href="/promos",
                                        style={"font-size": ".88rem", "color": "var(--ag-red)",
                                               "text-decoration": "none", "font-weight": "600"}),
                                class_name="ag-sidebar-widget",
                            ),
                            rx.el.div(
                                rx.el.div("Разделы", class_name="ag-sidebar-widget-title"),
                                rx.el.a("Новости", href="/news", class_name="ag-tag-pill d-block mb-2"),
                                rx.el.a("Акции", href="/promos", class_name="ag-tag-pill d-block mb-2"),
                                rx.el.a("Блог", href="/blog", class_name="ag-tag-pill d-block mb-2"),
                                class_name="ag-sidebar-widget",
                            ),
                        ),
                        class_name="col-lg-4",
                    ),
                    class_name="row g-5",
                ),
                class_name="container",
            ),
            class_name="ag-section-white ag-section-py",
            on_mount=ContentState.load_article_from_url,
        ),
        _footer(),
    )

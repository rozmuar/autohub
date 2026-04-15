"""Страница детали новости  Aigocy Style."""

import reflex as rx

from app.components.navbar import navbar
from app.pages.index import _footer
from app.pages.news import _sidebar
from app.states.content import ContentState


def news_detail_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    rx.el.a("Главная", href="/"), " / ",
                    rx.el.a("Новости", href="/news"), " / ",
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
                            rx.el.div(
                                rx.el.div(class_name="spinner-border text-secondary"),
                                class_name="text-center py-5",
                            ),
                            rx.el.div(
                                # Обложка
                                rx.cond(
                                    ContentState.art_cover_url,
                                    rx.el.img(
                                        src=ContentState.art_cover_url,
                                        alt=ContentState.art_title,
                                        class_name="ag-article-cover",
                                    ),
                                ),
                                # Мета
                                rx.el.div(
                                    rx.el.span(
                                        rx.el.i(class_name="bi bi-calendar3 me-1"),
                                        ContentState.art_published_at,
                                        style={"font-size": ".82rem", "color": "var(--ag-gray)"},
                                    ),
                                    rx.el.span(
                                        rx.el.i(class_name="bi bi-eye me-1"),
                                        ContentState.art_views_count,
                                        style={"font-size": ".82rem", "color": "var(--ag-gray)"},
                                    ),
                                    class_name="d-flex gap-3 mb-4 flex-wrap",
                                ),
                                # Контент
                                rx.el.div(
                                    rx.el.p(ContentState.art_body),
                                    class_name="ag-article",
                                ),
                                # Теги + шеринг
                                rx.el.div(
                                    rx.el.span("Новости", class_name="ag-tag-pill"),
                                    rx.el.span("Auto Hub", class_name="ag-tag-pill"),
                                    class_name="d-flex flex-wrap gap-2 mt-4",
                                ),
                            ),
                        ),
                        class_name="col-lg-8",
                    ),
                    # Сайдбар
                    rx.el.div(
                        rx.el.aside(
                            rx.el.div(
                                rx.el.div("Поиск", class_name="ag-sidebar-widget-title"),
                                rx.el.input(type="search", placeholder="Поиск по новостям", class_name="ag-form-control"),
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

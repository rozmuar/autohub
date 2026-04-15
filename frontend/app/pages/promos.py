"""Страница акций  Aigocy Style."""

import reflex as rx

from app.components.navbar import navbar
from app.pages.index import _footer, _label
from app.states.content import ContentState


def _promo_card(item) -> rx.Component:
    return rx.el.div(
        # Обложка
        rx.cond(
            item.cover_url,
            rx.el.img(src=item.cover_url, alt=item.title, class_name="ag-blog-card-img"),
            rx.el.div(
                rx.el.i(class_name="bi bi-percent", style={"font-size": "3rem", "color": "var(--ag-red)"}),
                style={"height": "180px", "background": "var(--ag-dark)", "display": "flex",
                       "align-items": "center", "justify-content": "center"},
            ),
        ),
        # Скидка-бейдж
        rx.cond(
            item.promo_discount_pct > 0,
            rx.el.div(
                rx.el.span("", item.promo_discount_pct, "%",
                           class_name="ag-blog-cat",
                           style={"background": "var(--ag-red)", "color": "white"}),
            ),
        ),
        rx.el.div(
            rx.el.div("Акция", class_name="ag-blog-cat"),
            rx.el.h5(
                rx.el.a(item.title, href="/promos/" + item.slug,
                        style={"color": "var(--ag-dark)", "text-decoration": "none",
                               "font-weight": "700", "font-size": "1rem"}),
                style={"margin": ".6rem 0 .4rem"},
            ),
            rx.cond(
                item.excerpt,
                rx.el.p(item.excerpt, style={"font-size": ".83rem", "color": "var(--ag-gray)",
                                             "margin-bottom": ".8rem",
                                             "display": "-webkit-box",
                                             "-webkit-line-clamp": "2",
                                             "-webkit-box-orient": "vertical",
                                             "overflow": "hidden"}),
            ),
            rx.cond(
                item.promo_valid_until,
                rx.el.div(
                    rx.el.i(class_name="bi bi-calendar3 me-1"),
                    "До: ", item.promo_valid_until,
                    style={"font-size": ".78rem", "color": "var(--ag-red)", "margin-bottom": ".8rem"},
                ),
            ),
            rx.el.a("Подробнее ", href="/promos/" + item.slug, class_name="ag-read-more"),
            class_name="ag-blog-card-body",
        ),
        class_name="ag-blog-card",
        style={"position": "relative"},
    )


def _sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div("Поиск", class_name="ag-sidebar-widget-title"),
            rx.el.input(type="search", placeholder="Поиск акций", class_name="ag-form-control"),
            class_name="ag-sidebar-widget",
        ),
        rx.el.div(
            rx.el.div("Актуальные акции", class_name="ag-sidebar-widget-title"),
            rx.foreach(
                ContentState.articles,
                lambda a: rx.el.a(
                    rx.el.div(a.title, style={"font-size": ".88rem", "font-weight": "600", "color": "var(--ag-dark)"}),
                    rx.cond(a.promo_valid_until,
                            rx.el.div("До: ", a.promo_valid_until, style={"font-size": ".75rem", "color": "var(--ag-red)"})),
                    href="/promos/" + a.slug,
                    class_name="ag-recent-post",
                ),
            ),
            class_name="ag-sidebar-widget",
        ),
    )


def _pagination() -> rx.Component:
    return rx.el.nav(
        rx.el.ul(
            rx.el.li(
                rx.el.button(rx.el.i(class_name="bi bi-chevron-left"),
                             on_click=ContentState.set_page_promo(ContentState.page - 1), class_name="page-link"),
                class_name=rx.cond(ContentState.page <= 1, "page-item disabled", "page-item"),
            ),
            rx.el.li(
                rx.el.span(ContentState.page, " / ", ContentState.pages, class_name="page-link text-muted"),
                class_name="page-item disabled",
            ),
            rx.el.li(
                rx.el.button(rx.el.i(class_name="bi bi-chevron-right"),
                             on_click=ContentState.set_page_promo(ContentState.page + 1), class_name="page-link"),
                class_name=rx.cond(ContentState.page >= ContentState.pages, "page-item disabled", "page-item"),
            ),
            class_name="pagination justify-content-center mt-4",
        ),
    )


def promotions_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.div(
            rx.el.div(
                rx.el.span(rx.el.a("Главная", href="/"), " / Акции", class_name="ag-breadcrumb"),
                class_name="mb-2",
            ),
            rx.el.h1("Акции и спецпредложения"),
            class_name="ag-page-header",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.cond(
                            ContentState.loading,
                            rx.el.div(rx.el.div(class_name="spinner-border text-secondary"), class_name="text-center py-5"),
                            rx.el.div(
                                rx.foreach(
                                    ContentState.articles,
                                    lambda item: rx.el.div(_promo_card(item), class_name="col-md-4"),
                                ),
                                class_name="row g-4",
                            ),
                        ),
                        _pagination(),
                        class_name="col-lg-9",
                    ),
                    rx.el.div(_sidebar(), class_name="col-lg-3"),
                    class_name="row g-5",
                ),
                class_name="container",
            ),
            class_name="ag-section-white ag-section-py",
            on_mount=ContentState.load_promos,
        ),
        _footer(),
    )

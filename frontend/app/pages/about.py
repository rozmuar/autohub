"""Страница О компании  Aigocy Style."""

import reflex as rx

from app.components.navbar import navbar
from app.pages.index import _footer, _label


def _team_card(name: str, role: str, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.i(class_name=f"bi {icon}", style={"font-size": "3.5rem", "color": "var(--ag-light)"}),
                style={"width": "100%", "height": "200px", "background": "var(--ag-bg)",
                       "display": "flex", "align-items": "center", "justify-content": "center"},
            ),
            rx.el.div(
                rx.el.div(name, class_name="name"),
                rx.el.div(role, class_name="role"),
                class_name="ag-team-card-body",
            ),
            class_name="ag-team-card",
        ),
        class_name="col-6 col-md-3",
    )


def _value(icon: str, title: str, text: str) -> rx.Component:
    return rx.el.div(
        rx.el.i(class_name=f"bi {icon}", style={"font-size": "1.8rem", "color": "var(--ag-red)", "margin-bottom": "1rem", "display": "block"}),
        rx.el.h5(title, style={"font-weight": "800", "margin-bottom": ".5rem"}),
        rx.el.p(text, style={"font-size": ".88rem", "color": "var(--ag-gray)", "margin": "0"}),
        class_name="ag-card ag-card-hover col-sm-6 col-lg-3",
    )


def about_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.div(
            rx.el.div(
                rx.el.span(rx.el.a("Главная", href="/"), " / О компании", class_name="ag-breadcrumb"),
                class_name="mb-2",
            ),
            rx.el.h1("О платформе Auto Hub"),
            class_name="ag-page-header",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.i(class_name="bi bi-car-front", style={"font-size": "2.5rem", "color": "var(--ag-red)"}),
                            rx.el.div(rx.el.div("10 000+", style={"font-size": "2.5rem", "font-weight": "900", "color": "white"}), rx.el.div("КЛИЕНТОВ", style={"font-size": ".7rem", "color": "rgba(255,255,255,.5)", "text-transform": "uppercase", "letter-spacing": ".1em"})),
                            rx.el.div(rx.el.div("500+", style={"font-size": "2.5rem", "font-weight": "900", "color": "white"}), rx.el.div("ПАРТНЁРОВ", style={"font-size": ".7rem", "color": "rgba(255,255,255,.5)", "text-transform": "uppercase", "letter-spacing": ".1em"})),
                            rx.el.div(rx.el.div("50к+", style={"font-size": "2.5rem", "font-weight": "900", "color": "white"}), rx.el.div("ЗАКАЗОВ", style={"font-size": ".7rem", "color": "rgba(255,255,255,.5)", "text-transform": "uppercase", "letter-spacing": ".1em"})),
                            class_name="d-flex flex-column gap-4 p-4",
                        ),
                        class_name="ag-card-dark h-100",
                        style={"min-height": "320px"},
                    ),
                    class_name="col-lg-5 mb-4",
                ),
                rx.el.div(
                    _label("О нас"),
                    rx.el.h2("Мы делаем авторемонт простым и честным"),
                    rx.el.p("Auto Hub  платформа, объединяющая автовладельцев и проверенные автосервисы. Мы берём на себя всё: от поиска до контроля качества работ.", style={"color": "var(--ag-gray)", "line-height": "1.7", "margin": "1rem 0"}),
                    rx.el.p("Каждый партнёр проходит верификацию. Отзывы публикуются только после выполненного заказа. Никакой рекламы  только честные оценки.", style={"color": "var(--ag-gray)", "line-height": "1.7"}),
                    rx.el.a("Найти сервис", href="/search", class_name="ag-btn-dark mt-3 d-inline-block"),
                    class_name="col-lg-7 mb-4",
                ),
                class_name="row g-5 align-items-center",
            ),
            class_name="container ag-section-py",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.div(_label("Принципы"), rx.el.h2("Наши ценности"), class_name="text-center mb-5"),
                rx.el.div(
                    _value("bi-patch-check", "Верификация", "Каждый сервис проходит проверку документов и репутации"),
                    _value("bi-currency-exchange", "Честные цены", "Стоимость фиксируется при записи. Без скрытых доплат"),
                    _value("bi-exclamation-triangle", "Экстренная помощь", "SOS-кнопка 24/7  помощь в любом месте"),
                    _value("bi-chat-dots", "Прямой диалог", "Чат с мастером без посредников и фото-отчёт"),
                    class_name="row g-4",
                ),
                class_name="container",
            ),
            class_name="ag-section-gray ag-section-py",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.div(_label("Команда"), rx.el.h2("Люди за платформой"), class_name="text-center mb-5"),
                rx.el.div(
                    _team_card("Алексей Волков", "CEO & Co-founder", "bi-person-circle"),
                    _team_card("Мария Иванова", "Директор по качеству", "bi-person"),
                    _team_card("Дмитрий Смирнов", "CTO", "bi-code-square"),
                    _team_card("Елена Козлова", "Head of Support", "bi-headset"),
                    class_name="row g-4",
                ),
                class_name="container",
            ),
            class_name="ag-section-white ag-section-py",
        ),
        rx.el.section(
            rx.el.div(
                _label("Начать"),
                rx.el.h2("Попробуйте Auto Hub ", rx.el.span("бесплатно", style={"color": "var(--ag-red)"})),
                rx.el.div(
                    rx.el.a("Зарегистрироваться", href="/register", class_name="ag-btn-dark me-3"),
                    rx.el.a("Найти сервис", href="/search", class_name="ag-btn-outline"),
                    class_name="ag-hero-actions mt-4",
                ),
                class_name="container ag-section-py",
            ),
            class_name="ag-section-gray",
        ),
        _footer(),
    )

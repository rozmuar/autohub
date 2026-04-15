"""Главная страница — AutoHub dark premium."""

import reflex as rx

from app.components.navbar import navbar
from app.state import AppState


def _label(text: str) -> rx.Component:
    return rx.el.div(
        rx.el.span(class_name="ah-hero-tag-dot"),
        text,
        class_name="ah-label",
    )


def _stat(num: str, suf: str, lbl: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(num, class_name="ah-stat-num"),
            rx.el.span(suf, class_name="ah-stat-suf"),
            style={"display": "flex", "align-items": "baseline", "justify-content": "center", "gap": ".2rem"},
        ),
        rx.el.span(lbl, class_name="ah-stat-label"),
        class_name="ah-stat-item",
    )


def _service(num: str, icon: str, title: str, desc: str, tags: list) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.i(class_name=f"bi {icon}", style={"font-size": "1.5rem", "color": "var(--c-red)", "flex-shrink": "0"}),
            rx.el.div(
                rx.el.div(num, style={"font-size": ".68rem", "font-weight": "700", "letter-spacing": ".08em", "color": "var(--c-gray2)", "margin-bottom": ".25rem"}),
                rx.el.h5(title, style={"font-size": "1.02rem", "font-weight": "700", "margin": "0 0 .4rem", "color": "var(--c-white)"}),
                rx.el.p(desc, style={"font-size": ".83rem", "color": "var(--c-gray)", "margin": "0 0 .75rem", "line-height": "1.5"}),
                rx.el.div(
                    *[rx.el.span(t, class_name="ag-service-tag") for t in tags],
                    class_name="ag-service-tags",
                ),
            ),
            class_name="d-flex align-items-start gap-3",
        ),
        class_name="ag-service-item",
    )


def _step(num: str, icon: str, title: str, desc: str, badge: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.i(class_name=f"bi {icon}", style={"font-size": "1.25rem"}),
                class_name="ah-step-icon",
            ),
            rx.el.span(badge, style={
                "background": "rgba(232,64,64,.1)", "border": "1px solid rgba(232,64,64,.2)",
                "border-radius": "50px", "padding": "2px 10px", "font-size": ".7rem",
                "font-weight": "700", "color": "var(--c-red)", "letter-spacing": ".06em",
                "margin-left": "auto",
            }),
            style={"display": "flex", "align-items": "center", "gap": ".75rem", "margin-bottom": "1rem"},
        ),
        rx.el.div(num, class_name="ah-step-num"),
        rx.el.h5(title, style={"font-size": "1rem", "font-weight": "700", "margin": "0 0 .5rem", "color": "var(--c-white)"}),
        rx.el.p(desc, style={"font-size": ".85rem", "color": "var(--c-gray)", "margin": "0", "line-height": "1.6"}),
        class_name="ah-step",
    )


def _footer() -> rx.Component:
    return rx.el.footer(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    "AUTO", rx.el.em("HUB"),
                    href="/",
                    class_name="ah-footer-logo",
                ),
                rx.el.p(
                    "Платформа для поиска надёжных автосервисов и онлайн-записи на обслуживание.",
                    class_name="ah-footer-desc",
                ),
                rx.el.div(
                    rx.el.a(rx.el.i(class_name="bi bi-telegram"), href="#", class_name="ah-footer-social"),
                    rx.el.a(rx.el.i(class_name="bi bi-vk"), href="#", class_name="ah-footer-social"),
                    rx.el.a(rx.el.i(class_name="bi bi-instagram"), href="#", class_name="ah-footer-social"),
                    style={"display": "flex", "gap": ".5rem", "margin-top": "1.25rem"},
                ),
                class_name="col-lg-4 mb-4",
            ),
            rx.el.div(
                rx.el.div("Сервисы", class_name="ah-footer-group-title"),
                rx.el.a("Найти сервис", href="/search", class_name="ah-footer-link"),
                rx.el.a("Как это работает", href="/#how-it-works", class_name="ah-footer-link"),
                rx.el.a("Записаться", href="/book", class_name="ah-footer-link"),
                rx.el.a("Экстренная помощь", href="/emergency", class_name="ah-footer-link"),
                class_name="col-6 col-lg-2 mb-4",
            ),
            rx.el.div(
                rx.el.div("Компания", class_name="ah-footer-group-title"),
                rx.el.a("О нас", href="/about", class_name="ah-footer-link"),
                rx.el.a("Новости", href="/news", class_name="ah-footer-link"),
                rx.el.a("Блог", href="/blog", class_name="ah-footer-link"),
                rx.el.a("Партнёрам", href="/partner/register", class_name="ah-footer-link"),
                class_name="col-6 col-lg-2 mb-4",
            ),
            rx.el.div(
                rx.el.div("Контакты", class_name="ah-footer-group-title"),
                rx.el.a("hello@autohub.ru", href="mailto:hello@autohub.ru", class_name="ah-footer-link"),
                rx.el.a("+7 800 000-00-00", href="tel:+78000000000", class_name="ah-footer-link"),
                rx.el.a("Контактная форма", href="/contacts", class_name="ah-footer-link"),
                class_name="col-lg-4 mb-4",
            ),
            class_name="row",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span("© 2026 AutoHub. Все права защищены.", class_name="ah-footer-copy"),
                rx.el.div(
                    rx.el.a("Политика конфиденциальности", href="#", class_name="ah-footer-bottom-link"),
                    rx.el.a("Оферта", href="#", class_name="ah-footer-bottom-link"),
                ),
                class_name="ah-footer-bottom-inner",
            ),
            class_name="ah-footer-bottom container",
        ),
        class_name="ah-footer",
    )


def index() -> rx.Component:
    return rx.el.div(
        navbar(),

        # ── HERO ─────────────────────────────────────────────────────
        rx.el.section(
            rx.el.div(class_name="ah-hero-grid"),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(class_name="ah-hero-tag-dot"),
                            "Автомобильная платформа #1 в России",
                            class_name="ah-hero-tag",
                        ),
                        rx.el.h1(
                            "Найдите лучший",
                            rx.el.br(),
                            "автосервис ",
                            rx.el.em("рядом"),
                            style={"margin-bottom": "1.5rem"},
                        ),
                        rx.el.p(
                            "Проверенные мастерские, честные цены, онлайн-запись и контроль заказов — всё в одном месте.",
                            style={"color": "var(--c-gray)", "font-size": "1.05rem", "max-width": "480px", "line-height": "1.7", "margin-bottom": "2.5rem"},
                        ),
                        rx.el.div(
                            rx.el.a("Найти сервис", href="/search", class_name="ah-btn ah-btn-primary ah-btn-lg"),
                            rx.el.a("Как это работает", href="#how-it-works", class_name="ah-btn ah-btn-ghost ah-btn-lg"),
                            style={"display": "flex", "gap": "1rem", "flex-wrap": "wrap"},
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.span("10 000+", style={"font-size": "1.1rem", "font-weight": "800", "color": "var(--c-white)"}),
                                rx.el.span("клиентов", style={"font-size": ".78rem", "color": "var(--c-gray)"}),
                                style={"display": "flex", "flex-direction": "column", "align-items": "center"},
                            ),
                            rx.el.div(style={"width": "1px", "height": "32px", "background": "var(--c-border)"}),
                            rx.el.div(
                                rx.el.span("500+", style={"font-size": "1.1rem", "font-weight": "800", "color": "var(--c-white)"}),
                                rx.el.span("партнёров", style={"font-size": ".78rem", "color": "var(--c-gray)"}),
                                style={"display": "flex", "flex-direction": "column", "align-items": "center"},
                            ),
                            rx.el.div(style={"width": "1px", "height": "32px", "background": "var(--c-border)"}),
                            rx.el.div(
                                rx.el.span("4.9", style={"font-size": "1.1rem", "font-weight": "800", "color": "var(--c-gold)"}),
                                rx.el.span("рейтинг", style={"font-size": ".78rem", "color": "var(--c-gray)"}),
                                style={"display": "flex", "flex-direction": "column", "align-items": "center"},
                            ),
                            class_name="ah-hero-stats",
                        ),
                        class_name="col-lg-6",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.i(class_name="bi bi-shield-check-fill", style={"font-size": "1.6rem", "color": "var(--c-red)"}),
                                rx.el.div(
                                    rx.el.div("Верифицированные партнёры", style={"font-weight": "700", "font-size": ".95rem", "color": "var(--c-white)"}),
                                    rx.el.div("Проверено командой AutoHub", style={"font-size": ".78rem", "color": "var(--c-gray)", "margin-top": ".15rem"}),
                                ),
                                style={"display": "flex", "align-items": "center", "gap": "1rem"},
                            ),
                            class_name="ah-glass",
                            style={"margin-bottom": "1rem"},
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.div("50 000+", style={"font-family": "'Syne',sans-serif", "font-size": "2.5rem", "font-weight": "900", "color": "var(--c-white)", "line-height": "1"}),
                                rx.el.div("ЗАКАЗОВ ВЫПОЛНЕНО", style={"font-size": ".68rem", "color": "var(--c-gray)", "letter-spacing": ".1em", "text-transform": "uppercase", "margin-top": ".4rem"}),
                            ),
                            rx.el.i(class_name="bi bi-stars", style={"font-size": "2.2rem", "color": "var(--c-gold)"}),
                            class_name="ah-glass",
                            style={"display": "flex", "align-items": "center", "justify-content": "space-between"},
                        ),
                        class_name="col-lg-5 offset-lg-1 d-none d-lg-block",
                    ),
                    class_name="row align-items-center",
                ),
                class_name="container position-relative",
            ),
            class_name="ah-hero",
        ),

        # ── STATS STRIP ──────────────────────────────────────────────
        rx.el.section(
            rx.el.div(
                _stat("10 000", "+", "Клиентов"),
                rx.el.div(class_name="ah-stats-sep"),
                _stat("500", "+", "Партнёров"),
                rx.el.div(class_name="ah-stats-sep"),
                _stat("50 000", "+", "Заказов"),
                rx.el.div(class_name="ah-stats-sep"),
                _stat("99", "%", "Довольных"),
                class_name="ah-stats-strip container",
            ),
        ),

        # ── SERVICES ─────────────────────────────────────────────────
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(class_name="ah-hero-tag-dot"),
                            "Что мы предлагаем",
                            class_name="ah-label",
                        ),
                        rx.el.h2(
                            "Всё необходимое",
                            rx.el.br(),
                            "для вашего авто",
                            style={"margin-bottom": "1rem"},
                        ),
                        rx.el.p(
                            "Мы объединяем водителей и лучшие автосервисы вашего города в единой платформе.",
                            style={"color": "var(--c-gray)", "max-width": "320px", "line-height": "1.65"},
                        ),
                        rx.el.a("Начать поиск", href="/search", class_name="ah-btn ah-btn-primary", style={"margin-top": "1.75rem", "display": "inline-flex"}),
                        class_name="col-lg-4 mb-4",
                    ),
                    rx.el.div(
                        _service("01", "bi-search", "Поиск сервисов", "Найдите ближайший автосервис по городу, специализации и рейтингу", ["По городу", "По услугам", "По рейтингу"]),
                        _service("02", "bi-calendar-check", "Онлайн-запись", "Запишитесь к мастеру в несколько кликов без звонков", ["Любое время", "Подтверждение"]),
                        _service("03", "bi-star", "Честные отзывы", "Реальные оценки от реальных клиентов после заказов", ["Верифицированные", "Только после заказа"]),
                        _service("04", "bi-exclamation-diamond", "Экстренная помощь", "SOS-кнопка для вызова помощи на дороге в любое время", ["24/7", "GPS-трекинг"]),
                        _service("05", "bi-chat-dots", "Чат с мастером", "Общайтесь с мастером напрямую до и во время ремонта", ["Реальное время", "Фото отчёт"]),
                        _service("06", "bi-grid", "Каталог запчастей", "Сравнивайте цены на запчасти от официальных поставщиков", ["Оригинал", "Аналоги"]),
                        class_name="col-lg-8",
                    ),
                    class_name="row g-4 align-items-start",
                ),
                class_name="container",
            ),
            class_name="ah-section",
            id="services",
        ),

        # ── HOW IT WORKS ─────────────────────────────────────────────
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(class_name="ah-hero-tag-dot"),
                            "Как это работает",
                            class_name="ah-label",
                        ),
                        rx.el.h2(
                            "Четыре шага",
                            rx.el.br(),
                            rx.el.em("до результата"),
                        ),
                        class_name="col-lg-3 mb-5",
                    ),
                    rx.el.div(_step("01", "bi-search", "Найдите сервис", "Введите город или услугу и выберите из списка проверенных сервисов", "1 мин"), class_name="col-sm-6 col-lg-3"),
                    rx.el.div(_step("02", "bi-calendar-plus", "Запишитесь", "Выберите удобное время и подтвердите запись прямо на сайте", "2 мин"), class_name="col-sm-6 col-lg-3"),
                    rx.el.div(_step("03", "bi-car-front", "Приедьте", "Мастер уже знает о вашем запросе и готов принять авто", "В назначенный час"), class_name="col-sm-6 col-lg-3"),
                    rx.el.div(_step("04", "bi-patch-check", "Получите отчёт", "Фото, комментарий мастера и чек — всё в личном кабинете", "После работ"), class_name="col-sm-6 col-lg-3"),
                    class_name="row g-4 align-items-start",
                ),
                class_name="container",
            ),
            class_name="ah-section",
            id="how-it-works",
            style={"background": "var(--c-bg1)"},
        ),

        # ── CTA ──────────────────────────────────────────────────────
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(class_name="ah-hero-tag-dot"),
                            "Начать бесплатно",
                            class_name="ah-label",
                        ),
                        rx.el.h2(
                            "Зарегистрируйтесь",
                            rx.el.br(),
                            "бесплатно сегодня",
                        ),
                        rx.el.p(
                            "Присоединяйтесь к 10 000+ водителям, которые уже пользуются AutoHub.",
                            style={"color": "var(--c-gray)", "margin-top": ".75rem", "font-size": ".95rem"},
                        ),
                        rx.el.div(
                            rx.el.a("Создать аккаунт", href="/register", class_name="ah-btn ah-btn-primary ah-btn-lg"),
                            rx.el.a("Стать партнёром", href="/partner/register", class_name="ah-btn ah-btn-outline ah-btn-lg"),
                            style={"display": "flex", "gap": "1rem", "flex-wrap": "wrap", "margin-top": "2rem"},
                        ),
                        class_name="col-lg-7",
                    ),
                    class_name="row",
                ),
                class_name="container",
            ),
            class_name="ah-section",
        ),

        _footer(),
    )
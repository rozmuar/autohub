"""Auto Hub — Reflex Frontend."""

import reflex as rx

from app.pages.index import index
from app.pages.login import login
from app.pages.register import register
from app.pages.search import search_page
from app.pages.profile import profile_page
from app.pages.garage import garage_page
from app.pages.orders import orders_page, order_detail_page
from app.pages.favorites import favorites_page
from app.pages.partner_detail import partner_detail_page
from app.pages.booking import booking_page
from app.pages.payment import payment_page, payment_success_page, payment_fail_page
from app.pages.emergency import emergency_page
from app.pages.chat import chat_page
from app.pages.partner.register import partner_register_page
from app.pages.partner.dashboard import partner_dashboard
from app.pages.partner.services import partner_services_page
from app.pages.partner.orders import partner_orders_page
from app.pages.partner.analytics import partner_analytics_page
from app.pages.partner.schedule import partner_schedule_page
from app.pages.news import news_page
from app.pages.news_detail import news_detail_page
from app.pages.promos import promotions_page
from app.pages.promo_detail import promo_detail_page
from app.pages.blog import blog_page
from app.pages.blog_detail import blog_detail_page
from app.pages.contacts import contacts_page
from app.pages.about import about_page
from app.state import AppState
from app.states.order import OrderState
from app.states.search import SearchState
from app.states.content import ContentState


def create_app() -> rx.App:
    app = rx.App(
        stylesheets=[
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
            "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
            "/styles/global.css",
        ],
        head_components=[
            rx.script(
                src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
            ),
        ],
        theme=rx.theme(
            appearance="light",
        ),
    )

    # Публичные страницы
    app.add_page(index, route="/", title="Auto Hub — Ваш автомобильный помощник")
    app.add_page(login, route="/login", title="Вход — Auto Hub")
    app.add_page(register, route="/register", title="Регистрация — Auto Hub")
    app.add_page(search_page, route="/search", title="Поиск — Auto Hub")
    app.add_page(partner_detail_page, route="/partners/[partner_id]", title="Партнёр — Auto Hub", on_load=SearchState.load_partner_from_url)

    # Пользовательские страницы
    app.add_page(profile_page, route="/profile", title="Профиль — Auto Hub")
    app.add_page(garage_page, route="/garage", title="Мой гараж — Auto Hub")
    app.add_page(orders_page, route="/orders", title="Заказы — Auto Hub")
    app.add_page(order_detail_page, route="/orders/[order_id]", title="Заказ — Auto Hub", on_load=OrderState.load_order_from_url)
    app.add_page(favorites_page, route="/favorites", title="Избранное — Auto Hub")
    app.add_page(booking_page, route="/booking", title="Запись — Auto Hub")
    app.add_page(payment_page, route="/payment/[order_id]", title="Оплата — Auto Hub")
    app.add_page(payment_success_page, route="/payment/success", title="Оплата прошла — Auto Hub")
    app.add_page(payment_fail_page, route="/payment/fail", title="Ошибка оплаты — Auto Hub")

    # Phase 2 — экстренная помощь и чат
    app.add_page(emergency_page, route="/emergency", title="Экстренная помощь — Auto Hub")
    app.add_page(chat_page, route="/chat", title="Сообщения — Auto Hub")

    # Партнёрские страницы
    app.add_page(partner_register_page, route="/partner/register", title="Стать партнёром — Auto Hub")
    app.add_page(partner_dashboard, route="/partner/dashboard", title="Кабинет партнёра — Auto Hub")
    app.add_page(partner_services_page, route="/partner/services", title="Услуги — Auto Hub")
    app.add_page(partner_orders_page, route="/partner/orders", title="Заказы партнёра — Auto Hub")
    app.add_page(partner_analytics_page, route="/partner/analytics", title="Аналитика — Auto Hub")
    app.add_page(partner_schedule_page, route="/partner/schedule", title="Расписание — Auto Hub")

    # Контент: новости, акции, блог
    app.add_page(news_page, route="/news", title="Новости — Auto Hub", on_load=ContentState.load_news)
    app.add_page(news_detail_page, route="/news/[slug]", title="Новость — Auto Hub", on_load=ContentState.load_article_from_url)
    app.add_page(promotions_page, route="/promotions", title="Акции — Auto Hub", on_load=ContentState.load_promos)
    app.add_page(promo_detail_page, route="/promotions/[slug]", title="Акция — Auto Hub", on_load=ContentState.load_article_from_url)
    app.add_page(blog_page, route="/blog", title="Блог — Auto Hub", on_load=ContentState.load_blog)
    app.add_page(blog_detail_page, route="/blog/[slug]", title="Блог — Auto Hub", on_load=ContentState.load_article_from_url)

    # Статичные страницы
    app.add_page(contacts_page, route="/contacts", title="Контакты — Auto Hub")
    app.add_page(about_page, route="/about", title="О компании — Auto Hub")

    return app


app = create_app()


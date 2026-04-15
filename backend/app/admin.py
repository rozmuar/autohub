"""SQLAdmin — административная панель.

Монтируется в FastAPI приложение через setup_admin(app).
Доступ: /admin  (защищён Basic-аутентификацией через settings.admin_secret_key).
"""

from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.config import settings
from app.core.db import async_engine
from app.models.booking import Booking, Slot
from app.models.catalog import (
    PartnerProduct,
    PartnerService,
    ProductCategory,
    ServiceCategory,
)
from app.models.chat import ChatMessage, ChatRoom
from app.models.emergency import EmergencyRequest, PartnerLocation
from app.models.notification import Notification
from app.models.order import Order, OrderItem
from app.models.partner import Partner, PartnerDocument
from app.models.payment import Payment, Payout, PromoCode
from app.models.review import Review, ReviewFlag
from app.models.user import User, UserSession
from app.models.vehicle import CarBrand, CarModel, Vehicle


class AdminAuth(AuthenticationBackend):
    """Простая Basic-аутентификация для /admin.

    В продакшне замените на OAuth2/SSO или IP-whitelist.
    """

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username", "")
        password = form.get("password", "")
        if username == settings.admin_username and password == settings.admin_secret_key:
            request.session["admin_authenticated"] = True
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("admin_authenticated", False)


# ── ModelView definitions ────────────────────────────────────────────────────

class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"
    column_list = ["id", "phone", "email", "full_name", "role", "is_active", "created_at"]
    column_searchable_list = ["phone", "email", "full_name"]
    column_sortable_list = ["created_at", "role"]
    column_default_sort = [("created_at", True)]
    can_delete = False  # Soft-delete только через API


class PartnerAdmin(ModelView, model=Partner):
    name = "Партнёр"
    name_plural = "Партнёры"
    icon = "fa-solid fa-store"
    column_list = ["id", "company_name", "status", "rating", "is_active", "created_at"]
    column_searchable_list = ["company_name", "inn"]
    column_sortable_list = ["created_at", "rating", "status"]
    column_default_sort = [("created_at", True)]


class OrderAdmin(ModelView, model=Order):
    name = "Заказ"
    name_plural = "Заказы"
    icon = "fa-solid fa-file-invoice"
    column_list = ["id", "status", "order_type", "final_amount", "client_id", "partner_id", "created_at"]
    column_sortable_list = ["created_at", "status", "final_amount"]
    column_default_sort = [("created_at", True)]
    can_create = False
    can_delete = False


class PaymentAdmin(ModelView, model=Payment):
    name = "Платёж"
    name_plural = "Платежи"
    icon = "fa-solid fa-credit-card"
    column_list = ["id", "status", "amount", "method", "order_id", "created_at"]
    column_sortable_list = ["created_at", "status", "amount"]
    column_default_sort = [("created_at", True)]
    can_create = False
    can_edit = False
    can_delete = False


class PromoCodeAdmin(ModelView, model=PromoCode):
    name = "Промокод"
    name_plural = "Промокоды"
    icon = "fa-solid fa-tag"
    column_list = ["id", "code", "discount_type", "discount_value", "is_active", "expires_at", "usage_count"]
    column_searchable_list = ["code"]
    column_sortable_list = ["created_at", "expires_at"]


class ReviewAdmin(ModelView, model=Review):
    name = "Отзыв"
    name_plural = "Отзывы"
    icon = "fa-solid fa-star"
    column_list = ["id", "rating", "status", "author_id", "partner_id", "created_at"]
    column_sortable_list = ["created_at", "rating", "status"]
    column_default_sort = [("created_at", True)]


class ReviewFlagAdmin(ModelView, model=ReviewFlag):
    name = "Жалоба на отзыв"
    name_plural = "Жалобы на отзывы"
    icon = "fa-solid fa-flag"
    column_list = ["id", "review_id", "reported_by_id", "reason", "is_resolved", "created_at"]
    column_sortable_list = ["created_at"]


class ServiceCategoryAdmin(ModelView, model=ServiceCategory):
    name = "Категория услуг"
    name_plural = "Категории услуг"
    icon = "fa-solid fa-list"
    column_list = ["id", "name", "slug", "is_active", "sort_order"]
    column_searchable_list = ["name", "slug"]


class ProductCategoryAdmin(ModelView, model=ProductCategory):
    name = "Категория товаров"
    name_plural = "Категории товаров"
    icon = "fa-solid fa-box"
    column_list = ["id", "name", "slug", "is_active", "sort_order"]


class EmergencyRequestAdmin(ModelView, model=EmergencyRequest):
    name = "Экстренная заявка"
    name_plural = "Экстренные заявки"
    icon = "fa-solid fa-truck-medical"
    column_list = ["id", "status", "emergency_type", "user_id", "accepted_partner_id", "created_at"]
    column_sortable_list = ["created_at", "status"]
    column_default_sort = [("created_at", True)]
    can_create = False
    can_edit = False
    can_delete = False


class NotificationAdmin(ModelView, model=Notification):
    name = "Уведомление"
    name_plural = "Уведомления"
    icon = "fa-solid fa-bell"
    column_list = ["id", "user_id", "channel", "status", "title", "created_at"]
    column_default_sort = [("created_at", True)]
    can_create = False
    can_delete = False


_VIEWS = [
    UserAdmin,
    PartnerAdmin,
    OrderAdmin,
    PaymentAdmin,
    PromoCodeAdmin,
    ReviewAdmin,
    ReviewFlagAdmin,
    ServiceCategoryAdmin,
    ProductCategoryAdmin,
    EmergencyRequestAdmin,
    NotificationAdmin,
]


def setup_admin(app: FastAPI) -> None:
    """Монтирует SQLAdmin к приложению FastAPI."""
    authentication_backend = AdminAuth(secret_key=settings.secret_key)
    admin = Admin(
        app,
        engine=async_engine,
        authentication_backend=authentication_backend,
        title="AutoHub Admin",
        base_url="/admin",
    )
    for view in _VIEWS:
        admin.add_view(view)

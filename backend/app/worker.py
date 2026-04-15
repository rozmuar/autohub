"""Celery приложение и конфигурация задач."""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

# Создание Celery приложения
celery_app = Celery(
    "autohub",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.notifications",
        "app.tasks.bookings",
        "app.tasks.payments",
        "app.tasks.search_index",
        "app.tasks.reviews",
        "app.tasks.emergency",
    ],
)

celery_app.conf.update(
    # Сериализация
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Временные зоны
    timezone="Europe/Moscow",
    enable_utc=True,

    # Надёжность
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,

    # Результаты
    result_expires=86400,  # 24 часа

    # Очереди
    task_default_queue="default",
    task_queues={
        "default": {},
        "notifications": {"exchange": "notifications"},
        "payments": {"exchange": "payments"},
        "search_index": {"exchange": "search_index"},
        "emergency": {"exchange": "emergency"},
    },

    # Маршрутизация задач по очередям
    task_routes={
        "app.tasks.notifications.*": {"queue": "notifications"},
        "app.tasks.payments.*": {"queue": "payments"},
        "app.tasks.search_index.*": {"queue": "search_index"},
        "app.tasks.emergency.*": {"queue": "emergency"},
    },

    # Повторы при сбоях
    task_max_retries=3,
    task_default_retry_delay=60,  # секунды

    # Beat расписание (периодические задачи)
    beat_schedule={
        # Освобождение истёкших бронирований каждые 2 минуты
        "release-expired-slots": {
            "task": "app.tasks.bookings.release_expired_slots",
            "schedule": 120,
        },
        # Отправка напоминаний каждые 15 минут
        "send-booking-reminders": {
            "task": "app.tasks.notifications.send_booking_reminders",
            "schedule": crontab(minute="*/15"),
        },
        # Переиндексация в Elasticsearch каждую ночь в 3:00
        "reindex-partners": {
            "task": "app.tasks.search_index.reindex_all_partners",
            "schedule": crontab(hour=3, minute=0),
        },
        # Запрос отзывов через 2ч после закрытия заказа — каждые 5 минут
        "request-reviews": {
            "task": "app.tasks.reviews.request_reviews_for_closed_orders",
            "schedule": crontab(minute="*/5"),
        },
        # Истечение откликов на экстренные заявки каждые 30 секунд
        "expire-emergency-responses": {
            "task": "app.tasks.emergency.expire_emergency_responses",
            "schedule": 30,
        },
    },
)

# Алиас для использования в задачах
worker = celery_app

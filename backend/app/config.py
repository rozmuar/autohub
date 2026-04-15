from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Общее ────────────────────────────────────────────────────
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = False
    secret_key: str = Field(min_length=32)
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]

    # ─── Сервер ───────────────────────────────────────────────────
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_workers: int = 1

    # ─── Database ─────────────────────────────────────────────────
    database_url: PostgresDsn
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_echo: bool = False

    # ─── Redis ────────────────────────────────────────────────────
    redis_url: RedisDsn = "redis://localhost:6379/0"  # type: ignore[assignment]
    redis_cache_ttl: int = 300
    redis_session_ttl: int = 2592000

    # ─── Celery ───────────────────────────────────────────────────
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ─── Elasticsearch ────────────────────────────────────────────
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_user: str = "elastic"
    elasticsearch_password: str = ""
    es_index_partners: str = "partners"
    es_index_services: str = "services"
    es_index_products: str = "products"

    # ─── S3 / MinIO ───────────────────────────────────────────────
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str
    s3_secret_key: str
    s3_region: str = "ru-central1"
    s3_bucket_media: str = "autohub-media"
    s3_bucket_docs: str = "autohub-docs"
    s3_public_url: str = "http://localhost:9000/autohub-media"

    # ─── JWT ──────────────────────────────────────────────────────
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30
    jwt_algorithm: str = "HS256"

    # ─── ЮKassa ───────────────────────────────────────────────────
    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""
    yookassa_return_url: str = ""
    yookassa_webhook_secret: str = ""

    # ─── SMS (smsc.ru) ────────────────────────────────────────────
    smsc_login: str = ""
    smsc_password: str = ""
    smsc_sender: str = "AutoHub"

    # ─── Email ────────────────────────────────────────────────────
    email_from: str = "noreply@autohub.ru"
    email_from_name: str = "Auto Hub"
    smtp_host: str = "smtp.yandex.ru"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_tls: bool = True

    # ─── Firebase FCM ─────────────────────────────────────────────
    firebase_project_id: str = ""
    firebase_credentials_path: str = "/secrets/firebase-credentials.json"

    # ─── Telegram ─────────────────────────────────────────────────
    telegram_bot_token: str = ""

    # ─── Яндекс Карты ─────────────────────────────────────────────
    yandex_maps_api_key: str = ""
    yandex_geocoder_api_key: str = ""

    # ─── Yandex Vision ────────────────────────────────────────────
    yandex_vision_folder_id: str = ""
    yandex_vision_api_key: str = ""

    # ─── GigaChat ─────────────────────────────────────────────────
    gigachat_client_id: str = ""
    gigachat_client_secret: str = ""

    # ─── Мониторинг ───────────────────────────────────────────────
    sentry_dsn: str = ""
    sentry_environment: str = "development"
    log_level: str = "INFO"

    # ─── RabbitMQ ─────────────────────────────────────────────────
    rabbitmq_url: str = "amqp://autohub:devpassword@localhost:5672/autohub"

    # ─── Admin Panel ──────────────────────────────────────────────
    admin_username: str = "admin"
    admin_secret_key: str = "changeme-admin-password"

    # ─── Computed Properties ──────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        # Гарантируем использование asyncpg драйвера
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()

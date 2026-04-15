"""Импорт автосервисов из yamap.csv в базу данных.

Запуск внутри контейнера:
    docker exec autohub_api python /app/app/seed_autoservices.py [--csv /path/to/yamap.csv] [--limit N]

Или с хоста (нужна БД):
    python app/seed_autoservices.py

CSV-формат (разделитель ;):
ID;Название;Регион;Город;Адрес;Индекс;Телефон;Мобильный телефон;Email;Сайт;
Рубрика;Подрубрика;Время работы;Способы оплаты;whatsapp;viber;telegram;
vkontakte;odnoklassniki;youtube;Факс;rutube;yandex zen;
Кол-во оценок;Рейтинг;Кол-во отзывов;Широта;Долгота
"""

import asyncio
import csv
import os
import sys
import uuid
import argparse
import logging

from sqlalchemy import select, func, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://autohub:devpassword@localhost:5432/autohub_db",
)

# Колонки CSV (0-based index)
COL_ID = 0
COL_NAME = 1
COL_REGION = 2
COL_CITY = 3
COL_ADDRESS = 4
COL_PHONE = 6
COL_MOBILE = 7
COL_EMAIL = 8
COL_WEBSITE = 9
COL_CATEGORY = 10
COL_SUBCATEGORY = 11
COL_HOURS = 12
COL_PAYMENT = 13
COL_WHATSAPP = 14
COL_TELEGRAM = 16
COL_VK = 17
COL_RATING_COUNT = 23
COL_RATING = 24
COL_REVIEWS = 25
COL_LAT = 26
COL_LON = 27

BATCH_SIZE = 200


def _get(row: list[str], idx: int) -> str | None:
    if idx < len(row):
        v = row[idx].strip()
        return v if v else None
    return None


def _float(val: str | None) -> float | None:
    if val is None:
        return None
    try:
        return float(val.replace(",", "."))
    except ValueError:
        return None


def _int(val: str | None) -> int:
    if val is None:
        return 0
    try:
        return int(val)
    except ValueError:
        return 0


def parse_row(row: list[str]) -> dict | None:
    """Парсит строку CSV в словарь для вставки в БД."""
    yamap_id = _get(row, COL_ID)
    name = _get(row, COL_NAME)
    if not yamap_id or not name:
        return None

    lat = _float(_get(row, COL_LAT))
    lon = _float(_get(row, COL_LON))

    phone = _get(row, COL_PHONE) or _get(row, COL_MOBILE) or "+70000000000"
    # Берём первый телефон если их несколько
    if phone and "," in phone:
        phone = phone.split(",")[0].strip()
    # Обрезаем до 20 символов
    phone = (phone or "+70000000000")[:20]

    email = _get(row, COL_EMAIL)
    # Берём первый email (бывают дубли через запятую)
    if email and "," in email:
        email = email.split(",")[0].strip()
    # Обрезаем очевидно невалидные адреса
    if email and (len(email) > 254 or "@" not in email):
        email = None

    rating_raw = _float(_get(row, COL_RATING)) or 0.0
    reviews_raw = _int(_get(row, COL_REVIEWS))

    city = _get(row, COL_CITY)
    region = _get(row, COL_REGION)

    # Если города нет — пробуем вытащить его из адреса
    address = _get(row, COL_ADDRESS)

    website = _get(row, COL_WEBSITE)
    if website and "," in website:
        website = website.split(",")[0].strip()
    if website and len(website) > 500:
        website = website[:500]

    telegram = _get(row, COL_TELEGRAM)
    if telegram and "," in telegram:
        telegram = telegram.split(",")[0].strip()
    if telegram and len(telegram) > 100:
        telegram = None

    return {
        "id": uuid.uuid4(),
        "yamap_id": yamap_id[:50],
        "name": name[:255],
        "description": None,
        "partner_type": "legal",
        "status": "active",
        "phone": phone,
        "email": email,
        "website": website,
        "telegram": telegram,
        "whatsapp": (_get(row, COL_WHATSAPP) or "")[:100] or None,
        "vkontakte": (_get(row, COL_VK) or "")[:300] or None,
        "city": (city or "")[:100] or None,
        "address": (address or "")[:500] or None,
        "region": (region or "")[:150] or None,
        "latitude": lat,
        "longitude": lon,
        "subcategory": (_get(row, COL_SUBCATEGORY) or "")[:500] or None,
        "working_hours": (_get(row, COL_HOURS) or "")[:300] or None,
        "payment_methods": _get(row, COL_PAYMENT),
        "rating": min(rating_raw, 5.0),
        "reviews_count": 0,
        "yamap_reviews_count": reviews_raw,
        "slots_count": 1,
        "commission_rate": 0.0,
        "is_imported": True,
        "subscription_plan": "free",
        "logo_url": None,
        "cover_url": None,
        "inn": None,
        "ogrn": None,
        "legal_name": None,
        "bank_account": None,
        "bank_bik": None,
        "rejection_reason": None,
        "verified_at": None,
        # owner_id: NULL — импортированные записи без владельца
    }


async def run(csv_path: str, limit: int | None = None, dry_run: bool = False) -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    SessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Загружаем CSV
    log.info("Reading CSV: %s", csv_path)
    rows: list[dict] = []
    with open(csv_path, encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        headers = next(reader)  # пропустить заголовок
        log.info("CSV columns: %d", len(headers))
        for i, raw in enumerate(reader):
            if limit and i >= limit:
                break
            rec = parse_row(raw)
            if rec:
                rows.append(rec)

    log.info("Parsed %d valid rows", len(rows))
    if dry_run:
        log.info("[DRY RUN] First record: %s", rows[0] if rows else "none")
        await engine.dispose()
        return

    async with SessionFactory() as db:
        # Узнаём, нужен ли owner_id (NOT NULL constraint)
        # В модели owner_id — nullable=False, но для импорта нужна система-пользователь
        # Создаём системного пользователя если не существует
        sys_user_id = await _ensure_system_user(db)
        log.info("System user id: %s", sys_user_id)

        # Получаем уже существующие yamap_id чтобы пропустить дубли
        result = await db.execute(
            text("SELECT yamap_id FROM partners WHERE yamap_id IS NOT NULL")
        )
        existing = {r[0] for r in result.fetchall()}
        log.info("Already imported: %d", len(existing))

        new_rows = [r for r in rows if r["yamap_id"] not in existing]
        log.info("New to import: %d", len(new_rows))

        # Проставляем owner_id
        for r in new_rows:
            r["owner_id"] = sys_user_id

        # Вставляем батчами
        inserted = 0
        for i in range(0, len(new_rows), BATCH_SIZE):
            batch = new_rows[i:i + BATCH_SIZE]
            await db.execute(
                text("""
                    INSERT INTO partners (
                        id, owner_id, yamap_id, name, description, partner_type, status,
                        phone, email, website, telegram, whatsapp, vkontakte,
                        city, address, region, latitude, longitude,
                        subcategory, working_hours, payment_methods,
                        rating, reviews_count, yamap_reviews_count,
                        slots_count, commission_rate, is_imported, subscription_plan,
                        logo_url, cover_url, inn, ogrn, legal_name,
                        bank_account, bank_bik, rejection_reason, verified_at,
                        created_at, updated_at
                    ) VALUES (
                        :id, :owner_id, :yamap_id, :name, :description, :partner_type, :status,
                        :phone, :email, :website, :telegram, :whatsapp, :vkontakte,
                        :city, :address, :region, :latitude, :longitude,
                        :subcategory, :working_hours, :payment_methods,
                        :rating, :reviews_count, :yamap_reviews_count,
                        :slots_count, :commission_rate, :is_imported, :subscription_plan,
                        :logo_url, :cover_url, :inn, :ogrn, :legal_name,
                        :bank_account, :bank_bik, :rejection_reason, :verified_at,
                        NOW(), NOW()
                    )
                    ON CONFLICT (yamap_id) DO NOTHING
                """),
                batch,
            )
            await db.commit()
            inserted += len(batch)
            log.info("Inserted %d / %d", inserted, len(new_rows))

    await engine.dispose()
    log.info("Import done.")


async def _ensure_system_user(db: AsyncSession) -> uuid.UUID:
    """Возвращает ID системного пользователя (создаёт если нет)."""
    result = await db.execute(
        text("SELECT id FROM users WHERE phone = :phone LIMIT 1"),
        {"phone": "+70000000000"},
    )
    row = result.fetchone()
    if row:
        return row[0]

    sys_id = uuid.uuid4()
    await db.execute(
        text("""
            INSERT INTO users (
                id, phone, role, is_active,
                is_phone_verified, is_email_verified, is_2fa_enabled,
                notify_sms, notify_email, notify_push, notify_telegram,
                created_at, updated_at
            )
            VALUES (
                :id, :phone, 'partner', true,
                false, false, false,
                true, true, true, false,
                NOW(), NOW()
            )
            ON CONFLICT (phone) DO NOTHING
        """),
        {"id": sys_id, "phone": "+70000000000"},
    )
    await db.commit()

    # Перечитываем — мог уже существовать
    result = await db.execute(
        text("SELECT id FROM users WHERE phone = :phone LIMIT 1"),
        {"phone": "+70000000000"},
    )
    row = result.fetchone()
    return row[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import autoservices from yamap.csv")
    parser.add_argument("--csv", default="/app/yamap.csv", help="Path to yamap.csv")
    parser.add_argument("--limit", type=int, default=None, help="Max rows to import")
    parser.add_argument("--dry-run", action="store_true", help="Parse without DB write")
    args = parser.parse_args()

    asyncio.run(run(args.csv, args.limit, args.dry_run))

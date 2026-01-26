# Auto Hub - Архитектура и алгоритмы работы системы

**Версия документа:** 1.0  
**Дата:** 26.01.2026  
**Статус:** Описание архитектуры на основе ТЗ v1.0

---

## Содержание

1. [Обзор системы](#1-обзор-системы)
2. [Архитектура платформы](#2-архитектура-платформы)
3. [Модули системы](#3-модули-системы)
4. [Алгоритмы работы](#4-алгоритмы-работы)
5. [Интеграции](#5-интеграции)
6. [Потоки данных](#6-потоки-данных)
7. [Безопасность и защита данных](#7-безопасность-и-защита-данных)

---

## 1. Обзор системы

### 1.1 Назначение

Auto Hub — единая цифровая платформа, связывающая:
- **Клиентов** (автовладельцев) — потребителей услуг и товаров
- **Партнёров** (автосервисы, магазины, эксперты) — поставщиков услуг и товаров
- **Администрацию платформы** — управление и модерация

### 1.2 Ключевые принципы

```
┌─────────────────────────────────────────────────────────────────┐
│                        AUTO HUB PLATFORM                        │
├─────────────────────────────────────────────────────────────────┤
│  КЛИЕНТ          ←→    ПЛАТФОРМА    ←→         ПАРТНЁР         │
│  ────────              ──────────              ─────────        │
│  • Поиск              • Матчинг               • Услуги          │
│  • Заказ              • Платежи               • Товары          │
│  • Оплата             • Логистика             • Календарь       │
│  • Отзывы             • AI-подбор             • Аналитика       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Архитектура платформы

### 2.1 Высокоуровневая архитектура

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           КЛИЕНТСКИЙ СЛОЙ                                │
├──────────────────────────────────────────────────────────────────────────┤
│                     Web Application (Python/Reflex)                      │
│                        или FastAPI + React/Vue                           │
│         ─────────────────────────────────────────────────────            │
│         📱 Mobile Apps (iOS/Android) — запланированы на v2.0             │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                            API GATEWAY                                    │
│                   (Rate Limiting, Auth, Routing)                         │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                          МИКРОСЕРВИСЫ                                     │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┤
│   Auth       │   User       │   Catalog    │   Order      │   Payment    │
│   Service    │   Service    │   Service    │   Service    │   Service    │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│   Partner    │   Booking    │   Search     │   Notify     │   AI/ML      │
│   Service    │   Service    │   Service    │   Service    │   Service    │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│   Chat       │   Review     │   Geo        │   Analytics  │   Expert     │
│   Service    │   Service    │   Service    │   Service    │   Service    │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           СЛОЙ ДАННЫХ                                     │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┤
│  PostgreSQL  │    Redis     │ Elasticsearch│  MongoDB     │     S3       │
│  (основная)  │   (кэш)      │   (поиск)    │  (логи/чат)  │   (файлы)    │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

### 2.2 Компоненты системы

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| Frontend Web | **Python (Reflex/NiceGUI)** или FastAPI + React | Веб-приложение для клиентов |
| Partner Portal | **Python (Reflex/Django)** | ЛК партнёра |
| Admin Panel | **Django Admin** или React Admin | Административная панель |
| Backend API | **FastAPI / Django REST** | REST API сервисы |
| API Gateway | Kong/Nginx | Маршрутизация, авторизация |
| Message Queue | RabbitMQ/Kafka (+ Celery) | Асинхронная обработка |
| Search Engine | Elasticsearch | Полнотекстовый поиск |
| Cache | Redis | Кэширование, сессии |
| Database | PostgreSQL | Основное хранилище |
| File Storage | S3/MinIO | Хранение файлов, изображений |
| Mobile Apps | React Native / Flutter | 📱 *Запланировано на v2.0* |

### 2.3 Варианты технологического стека на Python

**Вариант A: Full-Stack Python (рекомендуется для MVP)**
```
┌─────────────────────────────────────────────────────────────────┐
│                    FULL-STACK PYTHON                            │
├─────────────────────────────────────────────────────────────────┤
│  Frontend:  Reflex (Python) — компилируется в React             │
│  Backend:   FastAPI — высокопроизводительный async API          │
│  ORM:       SQLAlchemy 2.0 / Tortoise ORM                       │
│  Tasks:     Celery + Redis                                      │
│  Admin:     SQLAdmin / FastAPI-Admin                            │
└─────────────────────────────────────────────────────────────────┘
```

**Вариант B: Python Backend + JS Frontend**
```
┌─────────────────────────────────────────────────────────────────┐
│                 PYTHON + JAVASCRIPT                             │
├─────────────────────────────────────────────────────────────────┤
│  Frontend:  React / Vue.js / Next.js                            │
│  Backend:   FastAPI или Django REST Framework                   │
│  ORM:       SQLAlchemy / Django ORM                             │
│  Tasks:     Celery + Redis                                      │
│  Admin:     Django Admin                                        │
└─────────────────────────────────────────────────────────────────┘
```

**Вариант C: Django Monolith (быстрый старт)**
```
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO MONOLITH                              │
├─────────────────────────────────────────────────────────────────┤
│  Frontend:  Django Templates + HTMX + Alpine.js                 │
│  Backend:   Django + Django REST Framework                      │
│  ORM:       Django ORM                                          │
│  Tasks:     Celery + Redis                                      │
│  Admin:     Django Admin (встроенный)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Модули системы

### 3.1 Структура модулей

```
AUTO HUB
├── 🔐 AUTH MODULE (Аутентификация)
│   ├── Регистрация/Авторизация
│   ├── OAuth (Госуслуги, социальные сети)
│   ├── JWT токены
│   └── Двухфакторная аутентификация
│
├── 👤 USER MODULE (Пользователи)
│   ├── Профиль клиента
│   ├── Гараж (список автомобилей)
│   ├── История заказов
│   └── Избранное
│
├── 🚗 VEHICLE MODULE (Автомобили)
│   ├── OCR распознавание СТС/ПТС
│   ├── VIN декодер
│   ├── База марок/моделей
│   └── Совместимость запчастей
│
├── 🏢 PARTNER MODULE (Партнёры)
│   ├── Профиль партнёра
│   ├── Верификация документов
│   ├── Управление услугами/товарами
│   └── Календарь записи
│
├── 📦 CATALOG MODULE (Каталог)
│   ├── Услуги (категории, атрибуты)
│   ├── Товары (категории, атрибуты)
│   ├── Умные фильтры
│   └── Совместимость с авто
│
├── 🔍 SEARCH MODULE (Поиск)
│   ├── Полнотекстовый поиск
│   ├── Геопоиск партнёров
│   ├── Фильтрация и сортировка
│   └── Рекомендации
│
├── 📅 BOOKING MODULE (Бронирование)
│   ├── Календарь слотов
│   ├── Онлайн запись
│   ├── Управление расписанием
│   └── Напоминания
│
├── 🛒 ORDER MODULE (Заказы)
│   ├── Корзина
│   ├── Заказ-наряд
│   ├── Статусы заказов
│   └── История
│
├── 💳 PAYMENT MODULE (Платежи)
│   ├── Интеграция платёжных шлюзов
│   ├── Эскроу счета
│   ├── Комиссии платформы
│   └── Выплаты партнёрам
│
├── 🚨 EMERGENCY MODULE (Экстренная помощь)
│   ├── Геолокация в реальном времени
│   ├── Быстрый поиск партнёров
│   ├── Эвакуатор
│   └── Помощь на дороге
│
├── 🤖 AI MODULE (Умный подбор)
│   ├── OCR (распознавание текста)
│   ├── CV (распознавание деталей)
│   ├── NLP (обработка запросов)
│   └── Рекомендательная система
│
├── 💬 CHAT MODULE (Коммуникации)
│   ├── Чат клиент-партнёр
│   ├── Чат с экспертом
│   ├── Очередь запросов
│   └── Уведомления
│
├── ⭐ REVIEW MODULE (Отзывы)
│   ├── Рейтинги партнёров
│   ├── Рейтинги клиентов
│   ├── Модерация отзывов
│   └── Ответы на отзывы
│
├── 📊 ANALYTICS MODULE (Аналитика)
│   ├── Статистика партнёра
│   ├── Финансовые отчёты
│   └── Бизнес-аналитика
│
└── 🔔 NOTIFICATION MODULE (Уведомления)
    ├── Push-уведомления
    ├── Email
    ├── SMS
    └── Мессенджеры
```

---

## 4. Алгоритмы работы

### 4.1 Алгоритм идентификации автомобиля

```
┌─────────────────────────────────────────────────────────────────┐
│                 ИДЕНТИФИКАЦИЯ АВТОМОБИЛЯ                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Выбор способа  │
                    └─────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │  OCR фото   │    │  VIN ввод   │    │ Ручной ввод │
    │  СТС/ПТС    │    │             │    │             │
    └─────────────┘    └─────────────┘    └─────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │  AI модель  │    │ VIN декодер │    │   Форма     │
    │  извлечение │    │ API запрос  │    │  марка/     │
    │  данных     │    │ к базе      │    │  модель/год │
    └─────────────┘    └─────────────┘    └─────────────┘
           │                  │                  │
           └──────────────────┼──────────────────┘
                              ▼
                    ┌─────────────────┐
                    │  Валидация и    │
                    │  подтверждение  │
                    │  данных         │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Сохранение в   │
                    │  "Гараж" ЛК     │
                    └─────────────────┘
```

**Псевдокод OCR распознавания:**

```python
def identify_vehicle(input_data, method):
    """
    Алгоритм идентификации автомобиля
    
    Args:
        input_data: фото/VIN/данные формы
        method: 'ocr' | 'vin' | 'manual'
    
    Returns:
        VehicleData: структура с данными авто
    """
    
    if method == 'ocr':
        # 1. Предобработка изображения
        image = preprocess_image(input_data)
        
        # 2. Детекция области документа (СТС/ПТС)
        document_region = detect_document(image)
        
        # 3. OCR распознавание текста
        raw_text = ocr_extract(document_region)
        
        # 4. NLP извлечение сущностей
        entities = extract_entities(raw_text)
        # entities = {brand, model, year, vin, reg_number, ...}
        
        # 5. Валидация через внешнюю базу
        validated_data = validate_with_database(entities)
        
    elif method == 'vin':
        # 1. Валидация формата VIN (17 символов)
        if not validate_vin_format(input_data):
            raise ValidationError("Неверный формат VIN")
        
        # 2. Запрос к базе данных VIN
        validated_data = vin_decoder_api.decode(input_data)
        
    elif method == 'manual':
        # 1. Валидация введённых данных
        validated_data = validate_manual_input(input_data)
        
        # 2. Дополнение данных из каталога
        validated_data = enrich_from_catalog(validated_data)
    
    # Создание объекта Vehicle
    vehicle = Vehicle(
        brand=validated_data.brand,
        model=validated_data.model,
        year=validated_data.year,
        vin=validated_data.vin,
        engine_type=validated_data.engine_type,
        engine_volume=validated_data.engine_volume,
        transmission=validated_data.transmission
    )
    
    return vehicle
```

---

### 4.2 Алгоритм поиска и подбора услуг/товаров

```
┌─────────────────────────────────────────────────────────────────┐
│              ПОИСК И ПОДБОР УСЛУГ/ТОВАРОВ                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Выбор категории │
                    │ Услуги/Товары/  │
                    │ Запчасти        │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Загрузка данных │
                    │ авто из Гаража  │
                    └─────────────────┘
                              │
                              ▼
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │     УСЛУГИ      │             │ ТОВАРЫ/ЗАПЧАСТИ │
    └─────────────────┘             └─────────────────┘
              │                               │
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │ Пошаговый       │             │ Каталог с       │
    │ фильтр:         │             │ фильтрами:      │
    │ • Категория     │             │ • Категория     │
    │ • Тип работы    │             │ • Бренд         │
    │ • Доп. опции    │             │ • Цена          │
    │ • Свои запчасти?│             │ • Совместимость │
    └─────────────────┘             └─────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
                    ┌─────────────────┐
                    │  Формирование   │
                    │  поискового     │
                    │  запроса        │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Поиск партнёров │
                    │ по критериям:   │
                    │ • Геолокация    │
                    │ • Услуги/товары │
                    │ • Рейтинг       │
                    │ • Цена          │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Ранжирование    │
                    │ результатов     │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Отображение на  │
                    │ карте / списком │
                    └─────────────────┘
```

**Псевдокод поиска партнёров:**

```python
def search_partners(search_request):
    """
    Алгоритм поиска партнёров
    
    Args:
        search_request: {
            category: str,           # услуги/товары/запчасти
            service_ids: list,       # ID выбранных услуг
            product_ids: list,       # ID товаров
            vehicle_id: int,         # ID авто из гаража
            location: {lat, lng},    # координаты клиента
            radius: int,             # радиус поиска в км
            filters: dict,           # доп. фильтры
            sort_by: str             # сортировка
        }
    
    Returns:
        list[Partner]: список партнёров с рейтингом
    """
    
    # 1. Получение данных автомобиля
    vehicle = get_vehicle(search_request.vehicle_id)
    
    # 2. Формирование базового запроса
    query = ElasticSearchQuery()
    
    # 3. Фильтр по категории и услугам/товарам
    if search_request.category == 'services':
        query.filter('services.id', search_request.service_ids)
        # Фильтр совместимости услуги с авто
        query.filter('services.compatible_vehicles', vehicle.model_id)
    else:
        query.filter('products.id', search_request.product_ids)
        query.filter('products.compatible_vehicles', vehicle.model_id)
    
    # 4. Геофильтрация
    query.geo_distance(
        field='location',
        lat=search_request.location.lat,
        lng=search_request.location.lng,
        distance=f"{search_request.radius}km"
    )
    
    # 5. Фильтр активных партнёров
    query.filter('status', 'active')
    query.filter('is_verified', True)
    
    # 6. Применение дополнительных фильтров
    for key, value in search_request.filters.items():
        query.filter(key, value)
    
    # 7. Выполнение поиска
    results = elasticsearch.search(query)
    
    # 8. Обогащение данных
    partners = []
    for hit in results:
        partner = Partner.from_elastic(hit)
        
        # Расчёт расстояния
        partner.distance = calculate_distance(
            search_request.location,
            partner.location
        )
        
        # Получение актуальных цен
        partner.prices = get_partner_prices(
            partner.id,
            search_request.service_ids or search_request.product_ids
        )
        
        # Получение рейтинга
        partner.rating = get_partner_rating(partner.id)
        
        # Получение ближайших слотов (для услуг)
        if search_request.category == 'services':
            partner.available_slots = get_available_slots(
                partner.id,
                limit=3
            )
        
        partners.append(partner)
    
    # 9. Ранжирование
    partners = rank_partners(partners, search_request.sort_by)
    
    return partners


def rank_partners(partners, sort_by):
    """
    Алгоритм ранжирования партнёров
    
    Комплексный скоринг учитывает:
    - Рейтинг (40%)
    - Цена (25%)
    - Расстояние (20%)
    - Скорость записи (10%)
    - Акции (5%)
    """
    
    if sort_by == 'relevance':
        for partner in partners:
            partner.score = (
                partner.rating * 0.4 +
                (1 - normalize_price(partner.price)) * 0.25 +
                (1 - normalize_distance(partner.distance)) * 0.2 +
                availability_score(partner.available_slots) * 0.1 +
                (1 if partner.has_promo else 0) * 0.05
            )
        return sorted(partners, key=lambda p: p.score, reverse=True)
    
    elif sort_by == 'price':
        return sorted(partners, key=lambda p: p.price)
    
    elif sort_by == 'rating':
        return sorted(partners, key=lambda p: p.rating, reverse=True)
    
    elif sort_by == 'distance':
        return sorted(partners, key=lambda p: p.distance)
    
    return partners
```

---

### 4.3 Алгоритм оформления заказа на услугу

```
┌─────────────────────────────────────────────────────────────────┐
│                 ОФОРМЛЕНИЕ ЗАКАЗА НА УСЛУГУ                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Выбор партнёра  │
                    │ из результатов  │
                    │ поиска          │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Формирование    │
                    │ заявки:         │
                    │ • Основная      │
                    │   услуга        │
                    │ • Доп. услуги   │
                    │ • Свои запчасти?│
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Предварительный │
                    │ расчёт сметы    │──────────────────┐
                    │ (фиксация!)     │                  │
                    └─────────────────┘                  │
                              │                         │
                              ▼                         ▼
                    ┌─────────────────┐      ┌─────────────────┐
                    │ Выбор даты/     │      │   СМЕТА         │
                    │ времени из      │      │ сохраняется в   │
                    │ календаря       │      │ системе         │
                    │ партнёра        │      │ (лимит +15%)    │
                    └─────────────────┘      └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Выбор способа   │
                    │ оплаты:         │
                    │ • Полная        │
                    │ • Частичная     │
                    │ • При получении │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Подтверждение   │
                    │ заказа          │
                    └─────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │ Онлайн оплата   │             │ Оплата на месте │
    └─────────────────┘             └─────────────────┘
              │                               │
              ▼                               │
    ┌─────────────────┐                       │
    │ Платёжный шлюз  │                       │
    │ (ЮКасса/Яндекс) │                       │
    └─────────────────┘                       │
              │                               │
              └───────────────┬───────────────┘
                              ▼
                    ┌─────────────────┐
                    │ Создание        │
                    │ Заказ-Наряда    │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Уведомления:    │
                    │ • Клиенту       │
                    │ • Партнёру      │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Запись в        │
                    │ календарь       │
                    │ партнёра        │
                    └─────────────────┘
```

**Псевдокод оформления заказа:**

```python
class OrderService:
    
    def create_service_order(self, order_data):
        """
        Алгоритм создания заказа на услугу
        
        Args:
            order_data: {
                client_id: int,
                partner_id: int,
                vehicle_id: int,
                services: list[{service_id, quantity, own_parts}],
                slot_id: int,
                payment_type: str,
                promo_code: str
            }
        
        Returns:
            Order: созданный заказ
        """
        
        # 1. Валидация данных
        self._validate_order_data(order_data)
        
        # 2. Проверка доступности слота
        slot = self.booking_service.get_slot(order_data.slot_id)
        if not slot.is_available:
            raise SlotNotAvailableError()
        
        # 3. Формирование предварительной сметы
        estimate = self._calculate_estimate(
            partner_id=order_data.partner_id,
            services=order_data.services,
            vehicle_id=order_data.vehicle_id
        )
        
        # 4. Применение промокода
        if order_data.promo_code:
            estimate = self._apply_promo(estimate, order_data.promo_code)
        
        # 5. Создание заказа в БД
        order = Order(
            client_id=order_data.client_id,
            partner_id=order_data.partner_id,
            vehicle_id=order_data.vehicle_id,
            order_type='service',
            status='pending_payment',
            scheduled_at=slot.datetime,
            
            # Фиксация сметы (важно!)
            estimated_amount=estimate.total,
            max_allowed_amount=estimate.total * 1.15,  # +15% лимит
            
            services=order_data.services
        )
        
        db.save(order)
        
        # 6. Резервирование слота
        self.booking_service.reserve_slot(
            slot_id=slot.id,
            order_id=order.id
        )
        
        # 7. Обработка оплаты
        if order_data.payment_type == 'online_full':
            payment = self._process_payment(
                order_id=order.id,
                amount=estimate.total,
                type='full'
            )
        elif order_data.payment_type == 'online_partial':
            payment = self._process_payment(
                order_id=order.id,
                amount=estimate.total * 0.2,  # 20% предоплата
                type='partial'
            )
        else:
            # Оплата на месте
            payment = None
        
        # 8. Обновление статуса
        if payment and payment.status == 'success':
            order.status = 'confirmed'
            order.payment_id = payment.id
        else:
            order.status = 'awaiting_confirmation'
        
        db.save(order)
        
        # 9. Генерация Заказ-Наряда
        work_order = self._generate_work_order(order)
        
        # 10. Отправка уведомлений
        self.notification_service.send_order_confirmation(
            order=order,
            channels=['push', 'email', 'sms']
        )
        
        self.notification_service.send_new_order_to_partner(
            order=order,
            partner_id=order_data.partner_id
        )
        
        # 11. Планирование напоминаний
        self.scheduler.schedule_reminder(
            order_id=order.id,
            remind_at=slot.datetime - timedelta(hours=24),
            type='24h_before'
        )
        
        self.scheduler.schedule_reminder(
            order_id=order.id,
            remind_at=slot.datetime - timedelta(hours=2),
            type='2h_before'
        )
        
        return order
    
    
    def _calculate_estimate(self, partner_id, services, vehicle_id):
        """
        Расчёт предварительной сметы
        """
        estimate = Estimate()
        
        for service_item in services:
            service = self.catalog.get_service(service_item.service_id)
            
            # Получение цены партнёра
            partner_price = self.partner_service.get_price(
                partner_id=partner_id,
                service_id=service.id,
                vehicle_id=vehicle_id
            )
            
            estimate.add_item(
                name=service.name,
                quantity=service_item.quantity,
                price=partner_price.amount,
                type='service'
            )
            
            # Добавление запчастей если нужны
            if not service_item.own_parts and service.requires_parts:
                parts = self._get_required_parts(
                    service_id=service.id,
                    vehicle_id=vehicle_id
                )
                for part in parts:
                    estimate.add_item(
                        name=part.name,
                        quantity=part.quantity,
                        price=part.price,
                        type='part'
                    )
        
        estimate.calculate_totals()
        return estimate
```

---

### 4.4 Алгоритм изменения суммы заказа (правило +15%)

```
┌─────────────────────────────────────────────────────────────────┐
│             ИЗМЕНЕНИЕ СУММЫ ЗАКАЗА ПАРТНЁРОМ                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Партнёр вносит  │
                    │ изменения в     │
                    │ заказ           │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Расчёт новой    │
                    │ суммы           │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │  new_amount <=          │
                    │  estimated * 1.15 ?     │
                    └─────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │ ДА                         НЕТ│
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │ Автоматическое  │             │ Требуется       │
    │ применение      │             │ согласование    │
    │ изменений       │             │ клиента         │
    └─────────────────┘             └─────────────────┘
              │                               │
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │ Уведомление     │             │ Отправка        │
    │ клиенту об      │             │ запроса на      │
    │ изменении       │             │ согласование    │
    └─────────────────┘             └─────────────────┘
                                              │
                              ┌───────────────┴───────────────┐
                              ▼                               ▼
                    ┌─────────────────┐             ┌─────────────────┐
                    │ Клиент          │             │ Клиент          │
                    │ согласен        │             │ отказал         │
                    └─────────────────┘             └─────────────────┘
                              │                               │
                              ▼                               ▼
                    ┌─────────────────┐             ┌─────────────────┐
                    │ Применение      │             │ Выполнение в    │
                    │ изменений       │             │ рамках          │
                    └─────────────────┘             │ начальной сметы │
                                                   └─────────────────┘
```

**Псевдокод:**

```python
def update_order_amount(order_id, new_items, partner_id):
    """
    Алгоритм изменения суммы заказа с контролем +15%
    """
    order = get_order(order_id)
    
    # Проверка прав
    if order.partner_id != partner_id:
        raise PermissionDenied()
    
    # Расчёт новой суммы
    new_amount = calculate_new_amount(new_items)
    
    # Получение лимита (+15%)
    max_allowed = order.estimated_amount * 1.15
    
    if new_amount <= max_allowed:
        # Автоматическое применение
        order.current_amount = new_amount
        order.items = new_items
        order.amount_history.append({
            'timestamp': now(),
            'old_amount': order.current_amount,
            'new_amount': new_amount,
            'approved': True,
            'auto_approved': True
        })
        
        notify_client(
            order.client_id,
            type='order_amount_updated',
            message=f'Сумма заказа изменена: {new_amount}₽',
            order_id=order_id
        )
    else:
        # Требуется согласование
        approval_request = AmountApprovalRequest(
            order_id=order_id,
            requested_amount=new_amount,
            original_estimate=order.estimated_amount,
            difference=new_amount - order.estimated_amount,
            reason=extract_reason(new_items),
            status='pending'
        )
        
        db.save(approval_request)
        
        notify_client(
            order.client_id,
            type='amount_approval_required',
            message=f'Партнёр запросил изменение суммы заказа на {new_amount}₽',
            approval_request_id=approval_request.id,
            order_id=order_id
        )
        
        return approval_request
    
    db.save(order)
    return order
```

---

### 4.5 Алгоритм экстренной помощи

```
┌─────────────────────────────────────────────────────────────────┐
│                     ЭКСТРЕННАЯ ПОМОЩЬ                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Нажатие кнопки  │
                    │ "Экстренная"    │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Автоопределение │
                    │ геопозиции      │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Выбор типа      │
                    │ проблемы:       │
                    │ • Эвакуатор     │
                    │ • Прикурить     │
                    │ • Топливо       │
                    │ • Шиномонтаж    │
                    │ • Застрял       │
                    │ • Прочее        │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Уточняющие      │
                    │ вопросы:        │
                    │ • Тип авто      │
                    │ • КПП           │
                    │ • Есть провода? │
                    │ • и т.д.        │
                    └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BROADCAST ПОИСК                               │
│  Отправка push-уведомлений всем партнёрам в радиусе            │
│  (аналог Яндекс.Такси)                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Партнёры видят  │
                    │ заявку с        │
                    │ таймером        │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Первый принял - │
                    │ заказ его       │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Открытие канала │
                    │ связи:          │
                    │ • Чат           │
                    │ • Звонок        │
                    │ • Трекинг       │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Выполнение      │
                    │ услуги          │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Оплата по       │
                    │ тарифу/расчёту  │
                    └─────────────────┘
```

**Псевдокод:**

```python
class EmergencyService:
    
    SEARCH_RADIUS_KM = 15
    BROADCAST_TIMEOUT_SEC = 60
    
    async def create_emergency_request(self, request_data):
        """
        Алгоритм экстренной помощи
        
        Args:
            request_data: {
                client_id: int,
                location: {lat, lng},
                problem_type: str,  # 'tow', 'jumpstart', 'fuel', 'tire', 'stuck', 'other'
                vehicle_id: int,
                details: dict       # уточняющая информация
            }
        """
        
        # 1. Создание экстренной заявки
        emergency = EmergencyRequest(
            client_id=request_data.client_id,
            location=request_data.location,
            problem_type=request_data.problem_type,
            vehicle_id=request_data.vehicle_id,
            details=request_data.details,
            status='searching',
            created_at=now()
        )
        
        db.save(emergency)
        
        # 2. Поиск партнёров в радиусе
        partners = await self._find_emergency_partners(
            location=request_data.location,
            service_type=request_data.problem_type,
            radius_km=self.SEARCH_RADIUS_KM
        )
        
        if not partners:
            # Расширяем радиус
            partners = await self._find_emergency_partners(
                location=request_data.location,
                service_type=request_data.problem_type,
                radius_km=self.SEARCH_RADIUS_KM * 2
            )
        
        # 3. Broadcast уведомление всем партнёрам
        broadcast_id = await self._broadcast_emergency(
            emergency=emergency,
            partners=partners,
            timeout=self.BROADCAST_TIMEOUT_SEC
        )
        
        # 4. Ожидание ответа (WebSocket)
        accepted_partner = await self._wait_for_acceptance(
            broadcast_id=broadcast_id,
            timeout=self.BROADCAST_TIMEOUT_SEC
        )
        
        if accepted_partner:
            # 5. Партнёр принял заявку
            emergency.status = 'accepted'
            emergency.partner_id = accepted_partner.id
            emergency.accepted_at = now()
            
            # Расчёт ETA
            emergency.eta = calculate_eta(
                from_location=accepted_partner.current_location,
                to_location=emergency.location
            )
            
            db.save(emergency)
            
            # 6. Отмена broadcast для остальных
            await self._cancel_broadcast(broadcast_id)
            
            # 7. Создание канала связи
            chat = await self.chat_service.create_emergency_chat(
                client_id=emergency.client_id,
                partner_id=accepted_partner.id,
                emergency_id=emergency.id
            )
            
            # 8. Уведомление клиента
            await self.notification_service.send_push(
                user_id=emergency.client_id,
                title='Помощь в пути!',
                body=f'{accepted_partner.name} едет к вам. ETA: {emergency.eta} мин',
                data={
                    'type': 'emergency_accepted',
                    'emergency_id': emergency.id,
                    'chat_id': chat.id
                }
            )
            
            # 9. Запуск трекинга
            await self.tracking_service.start_tracking(
                partner_id=accepted_partner.id,
                emergency_id=emergency.id
            )
            
            return emergency
        
        else:
            # Никто не принял
            emergency.status = 'no_partners'
            db.save(emergency)
            
            await self.notification_service.send_push(
                user_id=emergency.client_id,
                title='Партнёры не найдены',
                body='К сожалению, рядом нет доступных партнёров. Попробуйте позже.'
            )
            
            return emergency
    
    
    async def _broadcast_emergency(self, emergency, partners, timeout):
        """
        Массовая рассылка экстренной заявки партнёрам
        """
        broadcast_id = generate_uuid()
        
        # Сохранение broadcast
        broadcast = EmergencyBroadcast(
            id=broadcast_id,
            emergency_id=emergency.id,
            partners=[p.id for p in partners],
            expires_at=now() + timedelta(seconds=timeout),
            status='active'
        )
        
        redis.set(
            f'emergency_broadcast:{broadcast_id}',
            broadcast.to_json(),
            ex=timeout
        )
        
        # Параллельная отправка push всем партнёрам
        tasks = []
        for partner in partners:
            distance = calculate_distance(
                emergency.location,
                partner.location
            )
            
            task = self.notification_service.send_push(
                user_id=partner.user_id,
                title='🚨 Экстренная заявка!',
                body=f'{emergency.problem_type_display} в {distance:.1f} км от вас',
                data={
                    'type': 'emergency_broadcast',
                    'broadcast_id': broadcast_id,
                    'emergency_id': emergency.id,
                    'timeout': timeout
                },
                priority='high',
                sound='emergency.wav'
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        return broadcast_id
```

---

### 4.6 Алгоритм AI-подбора запчастей

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI ПОДБОР ЗАПЧАСТЕЙ                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Выбор способа   │
                    │ подбора:        │
                    │ • AI (фото)     │
                    │ • Эксперт (чат) │
                    └─────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │   AI ПОДБОР     │             │ ЧАТ С ЭКСПЕРТОМ │
    └─────────────────┘             └─────────────────┘
              │                               │
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │ Загрузка фото   │             │ Запрос в        │
    │ или текстовый   │             │ очередь         │
    │ запрос          │             │ экспертов       │
    └─────────────────┘             └─────────────────┘
              │                               │
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │ Обработка:      │             │ Эксперт берёт   │
    │ • CV модель     │             │ запрос в работу │
    │   (фото)        │             └─────────────────┘
    │ • NLP модель    │                       │
    │   (текст)       │                       ▼
    └─────────────────┘             ┌─────────────────┐
              │                     │ Диалог в чате   │
              ▼                     │ (без контактов) │
    ┌─────────────────┐             └─────────────────┘
    │ Уточняющие      │                       │
    │ вопросы от AI   │◄──────────────────────┘
    └─────────────────┘
              │
              ▼
    ┌─────────────────┐
    │ Результат:      │
    │ • Название      │
    │ • Артикул       │
    │ • OEM номер     │
    │ • Совместимость │
    │ (БЕЗ ЦЕН!)      │
    └─────────────────┘
              │
              ▼
    ┌─────────────────┐
    │ Кнопка:         │
    │ "Показать       │
    │ предложения"    │
    └─────────────────┘
              │
              ▼
    ┌─────────────────┐
    │ API запросы к   │
    │ партнёрам       │
    │ (цены, наличие) │
    └─────────────────┘
              │
              ▼
    ┌─────────────────┐
    │ Список          │
    │ предложений     │
    │ с ценами        │
    └─────────────────┘
              │
              ▼
    ┌─────────────────┐
    │ Добавление в    │
    │ корзину, оплата │
    └─────────────────┘
```

**Псевдокод:**

```python
class AIPartsFinder:
    
    def __init__(self):
        self.cv_model = load_model('parts_classifier_v2')
        self.nlp_model = load_model('parts_nlp_v1')
        self.parts_database = PartsDatabase()
    
    async def find_part_by_image(self, image_data, vehicle_id):
        """
        AI подбор запчасти по фото
        
        Args:
            image_data: bytes изображения
            vehicle_id: ID авто из гаража
        
        Returns:
            PartSearchResult без цен!
        """
        
        # 1. Предобработка изображения
        processed_image = preprocess_image(image_data)
        
        # 2. Классификация типа детали
        part_predictions = self.cv_model.predict(processed_image)
        # [{'class': 'brake_disc', 'confidence': 0.87}, ...]
        
        top_prediction = part_predictions[0]
        
        if top_prediction.confidence < 0.6:
            # Низкая уверенность - нужно уточнение
            return PartSearchResult(
                status='needs_clarification',
                question='Это тормозной диск? Укажите: передний или задний?',
                options=['Передний', 'Задний']
            )
        
        # 3. Определение артикулов
        vehicle = get_vehicle(vehicle_id)
        
        matching_parts = self.parts_database.find_parts(
            part_type=top_prediction.class_name,
            vehicle_brand=vehicle.brand,
            vehicle_model=vehicle.model,
            vehicle_year=vehicle.year,
            engine_type=vehicle.engine_type
        )
        
        # 4. Формирование результата БЕЗ ЦЕН
        result = PartSearchResult(
            status='found',
            parts=[
                PartCandidate(
                    name=part.name,
                    article=part.article,
                    oem_number=part.oem_number,
                    compatibility_confirmed=True,
                    description=part.description,
                    image_url=part.image_url
                    # НЕТ ЦЕНЫ!
                )
                for part in matching_parts
            ],
            confidence=top_prediction.confidence,
            vehicle_info={
                'brand': vehicle.brand,
                'model': vehicle.model,
                'year': vehicle.year
            }
        )
        
        return result
    
    async def find_part_by_text(self, query, vehicle_id):
        """
        AI подбор запчасти по текстовому запросу
        """
        
        # 1. NLP обработка запроса
        entities = self.nlp_model.extract_entities(query)
        # entities = {part_type, position, brand_preference, ...}
        
        # 2. Определение что ищем
        intent = self.nlp_model.classify_intent(query)
        
        # 3. Генерация уточняющих вопросов если нужно
        if not entities.get('position') and requires_position(entities.part_type):
            return PartSearchResult(
                status='needs_clarification',
                question='Уточните расположение детали',
                options=['Передний левый', 'Передний правый', 
                        'Задний левый', 'Задний правый']
            )
        
        # 4. Поиск в базе
        vehicle = get_vehicle(vehicle_id)
        
        matching_parts = self.parts_database.search(
            query=query,
            entities=entities,
            vehicle=vehicle
        )
        
        # 5. Формирование результата
        return PartSearchResult(
            status='found',
            parts=[
                PartCandidate(
                    name=part.name,
                    article=part.article,
                    oem_number=part.oem_number,
                    compatibility_confirmed=True,
                    description=part.description
                )
                for part in matching_parts
            ]
        )
    
    async def get_price_offers(self, part_article, vehicle_id):
        """
        Получение предложений с ценами от партнёров
        Вызывается ТОЛЬКО после нажатия кнопки "Показать предложения"
        """
        
        # 1. Запросы к API партнёров
        partner_apis = get_active_partner_apis()
        
        offers = []
        tasks = []
        
        for api in partner_apis:
            task = api.search_part(
                article=part_article,
                vehicle_id=vehicle_id
            )
            tasks.append((api.partner_id, task))
        
        # 2. Параллельные запросы
        results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)
        
        # 3. Агрегация результатов
        for i, result in enumerate(results):
            partner_id = tasks[i][0]
            
            if isinstance(result, Exception):
                continue
            
            for item in result.items:
                offers.append(PartOffer(
                    partner_id=partner_id,
                    partner_name=get_partner_name(partner_id),
                    partner_rating=get_partner_rating(partner_id),
                    article=item.article,
                    brand=item.brand,
                    name=item.name,
                    price=item.price,  # Теперь показываем цену!
                    quantity=item.quantity,
                    delivery_days=item.delivery_days,
                    warranty_months=item.warranty_months
                ))
        
        # 4. Сортировка предложений
        offers = sorted(offers, key=lambda x: (x.price, -x.partner_rating))
        
        return offers


class ExpertChatService:
    """
    Сервис чата с экспертами-подборщиками
    """
    
    async def create_request(self, client_id, vehicle_id, description, images=None):
        """
        Создание запроса на подбор экспертом
        """
        
        request = ExpertRequest(
            client_id=client_id,
            vehicle_id=vehicle_id,
            description=description,
            images=images,
            status='in_queue',
            created_at=now()
        )
        
        db.save(request)
        
        # Добавление в очередь
        await redis.lpush('expert_queue', request.id)
        
        # Уведомление экспертов о новом запросе
        await self.notification_service.notify_experts(
            message='Новый запрос на подбор',
            request_id=request.id
        )
        
        return request
    
    async def expert_take_request(self, expert_id, request_id):
        """
        Эксперт берёт запрос в работу
        """
        
        # Проверка что запрос ещё свободен
        request = get_request(request_id)
        if request.status != 'in_queue':
            raise RequestAlreadyTakenError()
        
        # Атомарное взятие запроса
        taken = await redis.setnx(
            f'request_lock:{request_id}',
            expert_id,
            ex=3600
        )
        
        if not taken:
            raise RequestAlreadyTakenError()
        
        request.status = 'in_progress'
        request.expert_id = expert_id
        request.started_at = now()
        
        db.save(request)
        
        # Создание чата (контакты скрыты!)
        chat = Chat(
            type='expert_consultation',
            request_id=request_id,
            participants=[
                {'user_id': request.client_id, 'role': 'client'},
                {'user_id': expert_id, 'role': 'expert', 'display_name': 'Эксперт Auto Hub'}
            ],
            # Контактные данные НЕ передаются
            hide_contacts=True
        )
        
        db.save(chat)
        
        return chat
```

---

### 4.7 Алгоритм работы календаря и бронирования

```
┌─────────────────────────────────────────────────────────────────┐
│                УПРАВЛЕНИЕ КАЛЕНДАРЁМ ПАРТНЁРА                   │
└─────────────────────────────────────────────────────────────────┘

1. НАСТРОЙКА РАСПИСАНИЯ
   ┌─────────────────┐
   │ Партнёр задаёт: │
   │ • Рабочие дни   │
   │ • Часы работы   │
   │ • Перерывы      │
   │ • Выходные      │
   │ • Кол-во постов │
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │ Генерация       │
   │ слотов на       │
   │ период вперёд   │
   └─────────────────┘

2. РЕЗЕРВИРОВАНИЕ СЛОТА
   ┌─────────────────┐
   │ Клиент выбирает │
   │ время           │
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │ Проверка        │
   │ доступности     │
   │ (с блокировкой) │
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │ Временное       │
   │ резервирование  │
   │ (5 минут)       │
   └─────────────────┘
           │
           ▼
   ┌─────────────────┐
   │ Подтверждение   │
   │ или отмена      │
   └─────────────────┘

3. УПРАВЛЕНИЕ ЗАЯВКАМИ
   ┌─────────────────────────────────────────────────────────────┐
   │                    КАНБАН-ДОСКА                             │
   ├──────────────┬──────────────┬──────────────┬───────────────┤
   │    НОВЫЕ     │  В РАБОТЕ    │   ГОТОВО     │   ОТМЕНЕНО    │
   ├──────────────┼──────────────┼──────────────┼───────────────┤
   │  ┌────────┐  │  ┌────────┐  │  ┌────────┐  │  ┌────────┐   │
   │  │Заказ #1│  │  │Заказ #3│  │  │Заказ #5│  │  │Заказ #7│   │
   │  └────────┘  │  └────────┘  │  └────────┘  │  └────────┘   │
   │  ┌────────┐  │  ┌────────┐  │  ┌────────┐  │               │
   │  │Заказ #2│  │  │Заказ #4│  │  │Заказ #6│  │               │
   │  └────────┘  │  └────────┘  │  └────────┘  │               │
   └──────────────┴──────────────┴──────────────┴───────────────┘
```

**Псевдокод:**

```python
class BookingService:
    
    def generate_slots(self, partner_id, date_range):
        """
        Генерация слотов на основе расписания партнёра
        """
        schedule = get_partner_schedule(partner_id)
        partner = get_partner(partner_id)
        
        slots = []
        
        for date in date_range:
            # Проверка рабочего дня
            if date.weekday() not in schedule.working_days:
                continue
            
            # Проверка исключений (праздники, отпуск)
            if date in schedule.exceptions:
                continue
            
            # Генерация слотов на день
            current_time = schedule.start_time
            
            while current_time < schedule.end_time:
                # Проверка перерывов
                if not is_in_break(current_time, schedule.breaks):
                    
                    # Создание слота для каждого поста/мастера
                    for post_id in range(1, partner.posts_count + 1):
                        slot = TimeSlot(
                            partner_id=partner_id,
                            date=date,
                            start_time=current_time,
                            end_time=current_time + schedule.slot_duration,
                            post_id=post_id,
                            status='available'
                        )
                        slots.append(slot)
                
                current_time += schedule.slot_duration
        
        db.bulk_insert(slots)
        return slots
    
    async def reserve_slot(self, slot_id, client_id, order_id=None):
        """
        Резервирование слота с распределённой блокировкой
        """
        
        # 1. Распределённая блокировка
        lock_key = f'slot_lock:{slot_id}'
        lock_acquired = await redis.setnx(lock_key, client_id, ex=300)  # 5 минут
        
        if not lock_acquired:
            raise SlotAlreadyReservedError()
        
        try:
            # 2. Проверка статуса слота в БД
            slot = db.get(TimeSlot, slot_id, for_update=True)
            
            if slot.status != 'available':
                raise SlotNotAvailableError()
            
            # 3. Резервирование
            slot.status = 'reserved'
            slot.reserved_by = client_id
            slot.reserved_at = now()
            slot.reservation_expires_at = now() + timedelta(minutes=5)
            slot.order_id = order_id
            
            db.save(slot)
            
            # 4. Планирование автоотмены если не подтверждено
            scheduler.schedule(
                task=self.auto_release_slot,
                args=[slot_id],
                run_at=slot.reservation_expires_at
            )
            
            return slot
            
        except Exception as e:
            await redis.delete(lock_key)
            raise e
    
    async def confirm_slot(self, slot_id, order_id):
        """
        Подтверждение слота после оплаты
        """
        slot = db.get(TimeSlot, slot_id, for_update=True)
        
        if slot.status != 'reserved':
            raise SlotNotReservedError()
        
        slot.status = 'confirmed'
        slot.order_id = order_id
        slot.confirmed_at = now()
        
        db.save(slot)
        
        # Уведомление партнёра
        await notification_service.send_to_partner(
            partner_id=slot.partner_id,
            type='new_booking',
            data={
                'slot_id': slot_id,
                'order_id': order_id,
                'datetime': f'{slot.date} {slot.start_time}'
            }
        )
        
        return slot
```

---

## 5. Интеграции

### 5.1 Схема внешних интеграций (Российские сервисы)

```
┌─────────────────────────────────────────────────────────────────┐
│                      AUTO HUB PLATFORM                          │
└─────────────────────────────────────────────────────────────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
    ▼                         ▼                         ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  ПЛАТЕЖИ    │       │  КАРТЫ/ГЕО  │       │  КАТАЛОГИ   │
│  (РФ)       │       │  (РФ)       │       │  ЗАПЧАСТЕЙ  │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ • ЮКасса    │       │ • 2ГИС API  │       │ • Exist     │
│ • Т-Банк    │       │ • Яндекс    │       │ • EMEX      │
│ • СБП       │       │   Карты     │       │ • Autodoc   │
│ • CloudPay  │       │ • DaData    │       │ • Авто.ру   │
└─────────────┘       └─────────────┘       └─────────────┘
    │                         │                         │
    ▼                         ▼                         ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│УВЕДОМЛЕНИЯ  │       │    ГОС.     │       │   OCR/AI    │
│  (РФ)       │       │  СЕРВИСЫ    │       │   (РФ)      │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ • SMS Центр │       │ • ЕСИА      │       │ • Yandex    │
│ • Unisender │       │   (Госусл.) │       │   Vision    │
│ • RuStore   │       │ • ГИБДД     │       │ • Sber AI   │
│ • VK Push   │       │ • ФНС       │       │ • GigaChat  │
└─────────────┘       └─────────────┘       └─────────────┘
    │                         │                         │
    ▼                         ▼                         ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  ХОСТИНГ    │       │  ХРАНИЛИЩЕ  │       │ МЕССЕНДЖЕРЫ │
│  (РФ)       │       │  (РФ)       │       │   (РФ)      │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ • Yandex    │       │ • Yandex    │       │ • Telegram  │
│   Cloud     │       │   Object    │       │ • VK        │
│ • VK Cloud  │       │   Storage   │       │ • WhatsApp  │
│ • Selectel  │       │ • Selectel  │       │   Business  │
└─────────────┘       └─────────────┘       └─────────────┘
```

### 5.2 Детальный список сервисов (РФ)

#### 💳 ПЛАТЕЖНЫЕ СИСТЕМЫ

| Сервис | Назначение | Комиссия | Особенности |
|--------|------------|----------|-------------|
| **ЮKassa** | Основной эквайринг | 2.8-3.5% | Сплит-платежи, маркетплейс, выплаты |
| **Т-Банк (Тинькофф)** | Альтернативный эквайринг | 2.49-2.99% | Быстрое подключение, API |
| **СБП (Система быстрых платежей)** | Оплата по QR | 0.4-0.7% | Низкая комиссия, через НСПК |
| **CloudPayments** | Рекуррентные платежи | 2.7-3.2% | Подписки, автоплатежи |
| **Robokassa** | Универсальный агрегатор | 3.5-5% | Много способов оплаты |
| **SberPay** | Оплата через Сбер | 1.5-2% | Большая аудитория |

**Рекомендация:** ЮKassa как основной (поддержка маркетплейса) + СБП для низкой комиссии

---

#### 🗺️ КАРТЫ И ГЕОЛОКАЦИЯ

| Сервис | Назначение | Стоимость | API |
|--------|------------|-----------|-----|
| **Яндекс Карты** | Карты, маршруты, геокодер | от 0₽ (лимиты) | JS API, HTTP API |
| **2ГИС** | Карты, справочник организаций | от 0₽ (лимиты) | JS API, HTTP API |
| **DaData** | Подсказки адресов, валидация | от 0₽ (лимиты) | REST API |
| **ФИАС (ФНС)** | Официальный справочник адресов | Бесплатно | SOAP/REST |

**Рекомендация:** Яндекс Карты (карты) + DaData (подсказки адресов)

---

#### 📱 SMS И PUSH-УВЕДОМЛЕНИЯ

| Сервис | Назначение | Стоимость | Особенности |
|--------|------------|-----------|-------------|
| **SMS Центр (smsc.ru)** | SMS рассылки | от 1.5₽/SMS | Надёжный, API |
| **SMS.ru** | SMS рассылки | от 1.9₽/SMS | Простой API |
| **Devino Telecom** | SMS + Viber | от 1.3₽/SMS | Каскадные рассылки |
| **RuStore Push** | Push Android (РФ) | Бесплатно | Альтернатива FCM |
| **Huawei Push Kit** | Push Huawei | Бесплатно | Для устройств Huawei |
| **VK Push** | Push через VK | Бесплатно | Для пользователей VK |

**Рекомендация:** SMS Центр (SMS) + RuStore Push (Android) + APNs (iOS)

---

#### 📧 EMAIL РАССЫЛКИ

| Сервис | Назначение | Стоимость | Особенности |
|--------|------------|-----------|-------------|
| **Unisender** | Email маркетинг | от 0₽ (лимиты) | Российский, GDPR |
| **SendPulse** | Email + чат-боты | от 0₽ (лимиты) | Мультиканальный |
| **Dashamail** | Транзакционные письма | от 500₽/мес | Российский |
| **Почта Mail.ru для бизнеса** | Корпоративная почта | Бесплатно | Домен + SMTP |

**Рекомендация:** Unisender (маркетинг) + собственный SMTP (транзакционные)

---

#### 🤖 OCR И AI СЕРВИСЫ

| Сервис | Назначение | Стоимость | Особенности |
|--------|------------|-----------|-------------|
| **Yandex Vision** | OCR, распознавание документов | от 0₽ (лимиты) | СТС, ПТС, паспорт |
| **Yandex SpeechKit** | Голос → текст, текст → голос | от 0₽ (лимиты) | Русский язык |
| **GigaChat (Сбер)** | LLM чат-бот | от 0₽ (лимиты) | Российский GPT |
| **YandexGPT** | LLM, генерация текста | от 0₽ (лимиты) | NLP задачи |
| **Sber AI Vision** | Распознавание изображений | По запросу | CV модели |

**Рекомендация:** Yandex Vision (OCR документов) + GigaChat/YandexGPT (NLP)

---

#### 🏛️ ГОСУДАРСТВЕННЫЕ СЕРВИСЫ

| Сервис | Назначение | Доступ | Документация |
|--------|------------|--------|--------------|
| **ЕСИА (Госуслуги)** | Авторизация через Госуслуги | Заявка на подключение | esia.gosuslugi.ru |
| **ГИБДД API** | Проверка авто по VIN/госномеру | Ограниченный | гибдд.рф |
| **ФНС (ЕГРЮЛ/ЕГРИП)** | Проверка ИНН партнёров | Бесплатно | egrul.nalog.ru |
| **ФИАС** | Справочник адресов | Бесплатно | fias.nalog.ru |

**Рекомендация:** ЕСИА для авторизации (доверие пользователей) + ФНС для верификации партнёров

---

#### 🚗 БАЗЫ ДАННЫХ АВТОМОБИЛЕЙ И ЗАПЧАСТЕЙ

| Сервис | Назначение | Доступ | API |
|--------|------------|--------|-----|
| **Exist.ru** | Каталог запчастей, цены | Партнёрский | REST API |
| **EMEX** | Каталог запчастей | Партнёрский | REST API |
| **Autodoc** | Каталог запчастей | Партнёрский | REST API |
| **Авто.ру** | База авто, VIN декодер | Партнёрский | REST API |
| **Дром** | База авто | Ограниченный | - |
| **TecDoc** | Международный каталог | Лицензия | Web Service |
| **Laximo** | VIN декодер | Лицензия | SOAP/REST |

**Рекомендация:** Авто.ру (VIN) + Exist/EMEX API (запчасти)

---

#### ☁️ ОБЛАЧНЫЕ ПЛАТФОРМЫ (РФ)

| Сервис | Назначение | Особенности |
|--------|------------|-------------|
| **Yandex Cloud** | Полный стек (VM, DB, S3, Kubernetes) | 152-ФЗ, хранение в РФ |
| **VK Cloud** | Полный стек | 152-ФЗ |
| **Selectel** | VPS, выделенные серверы, S3 | Низкие цены |
| **Cloud.ru (SberCloud)** | Enterprise облако | 152-ФЗ, ГосОблако |
| **Timeweb Cloud** | VPS, хостинг | Бюджетный вариант |

**Рекомендация:** Yandex Cloud (полный стек, Managed PostgreSQL, S3)

---

#### 📊 АНАЛИТИКА И МОНИТОРИНГ

| Сервис | Назначение | Стоимость |
|--------|------------|-----------|
| **Яндекс Метрика** | Веб-аналитика | Бесплатно |
| **AppMetrica** | Мобильная аналитика | Бесплатно |
| **Roistat** | Сквозная аналитика | от 7000₽/мес |

---

#### 💬 МЕССЕНДЖЕРЫ И ЧАТ-БОТЫ

| Сервис | Назначение | API |
|--------|------------|-----|
| **Telegram Bot API** | Уведомления, бот | Бесплатно |
| **VK API** | Сообщества, уведомления | Бесплатно |
| **WhatsApp Business API** | Бизнес-коммуникации | Платно (через провайдера) |
| **Jivo** | Онлайн-консультант | от 0₽ |
| **Carrot Quest** | Чат + CRM | от 1000₽/мес |

---

### 5.3 Минимальный набор для MVP

```
┌─────────────────────────────────────────────────────────────────┐
│                    MVP - ОБЯЗАТЕЛЬНЫЕ СЕРВИСЫ                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  💳 ПЛАТЕЖИ:        ЮKassa (основной) + СБП                     │
│                                                                 │
│  🗺️ КАРТЫ:          Яндекс Карты + DaData                       │
│                                                                 │
│  📱 УВЕДОМЛЕНИЯ:    SMS Центр + Email (Unisender)               │
│                                                                 │
│  🤖 OCR:            Yandex Vision (СТС/ПТС)                     │
│                                                                 │
│  ☁️ ХОСТИНГ:        Yandex Cloud (VM + PostgreSQL + S3)         │
│                                                                 │
│  📊 АНАЛИТИКА:      Яндекс Метрика                              │
│                                                                 │
│  💬 КОММУНИКАЦИИ:   Telegram Bot                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.4 Оценка стоимости внешних сервисов (MVP)

| Сервис | Тариф | Стоимость/мес |
|--------|-------|---------------|
| Yandex Cloud (VM + DB + S3) | Стартовый | ~15,000 ₽ |
| ЮKassa | Комиссия с оборота | 2.8-3.5% |
| Яндекс Карты | До 25,000 запросов | Бесплатно |
| DaData | До 10,000 запросов | Бесплатно |
| Yandex Vision | До 1,000 запросов | Бесплатно |
| SMS Центр | ~1000 SMS | ~1,500 ₽ |
| Unisender | До 1,500 подписчиков | Бесплатно |
| Яндекс Метрика | Безлимит | Бесплатно |
| **ИТОГО (фикс)** | | **~16,500 ₽/мес** |

---

## 6. Потоки данных

### 6.1 Жизненный цикл заказа на услугу

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     ЖИЗНЕННЫЙ ЦИКЛ ЗАКАЗА                                │
└──────────────────────────────────────────────────────────────────────────┘

  КЛИЕНТ                 ПЛАТФОРМА                ПАРТНЁР
    │                        │                        │
    │  1. Создание заявки    │                        │
    │──────────────────────► │                        │
    │                        │  2. Уведомление        │
    │                        │──────────────────────► │
    │                        │                        │
    │                        │  3. Подтверждение      │
    │                        │◄────────────────────── │
    │  4. Статус: confirmed  │                        │
    │◄────────────────────── │                        │
    │                        │                        │
    │  5. Напоминание (-24ч) │                        │
    │◄────────────────────── │                        │
    │                        │                        │
    │  6. Визит              │                        │
    │─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─►│
    │                        │                        │
    │                        │  7. Статус: in_progress│
    │                        │◄────────────────────── │
    │  8. Push: в работе     │                        │
    │◄────────────────────── │                        │
    │                        │                        │
    │                        │  9. Завершение работ   │
    │                        │◄────────────────────── │
    │                        │                        │
    │  10. Запрос оплаты     │                        │
    │◄────────────────────── │                        │
    │                        │                        │
    │  11. Оплата            │                        │
    │──────────────────────► │                        │
    │                        │  12. Уведомление       │
    │                        │──────────────────────► │
    │                        │                        │
    │  13. Чек + заказ-наряд │                        │
    │◄────────────────────── │                        │
    │                        │                        │
    │  14. Запрос отзыва     │                        │
    │◄────────────────────── │                        │
    │                        │                        │
    │  15. Отзыв             │                        │
    │──────────────────────► │                        │
    │                        │  16. Уведомление       │
    │                        │──────────────────────► │
    │                        │                        │
```

### 6.2 Статусная модель заказа

```
                                    ┌─────────┐
                                    │ СОЗДАН  │
                                    │ created │
                                    └────┬────┘
                                         │
                            ┌────────────┴────────────┐
                            ▼                         ▼
                    ┌───────────────┐       ┌───────────────┐
                    │ ОЖИДАЕТ       │       │ ОТКЛОНЁН      │
                    │ ОПЛАТЫ        │       │ rejected      │
                    │ pending_pay   │       └───────────────┘
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ ПОДТВЕРЖДЁН   │
                    │ confirmed     │◄────────────────────┐
                    └───────┬───────┘                     │
                            │                             │
                            ▼                             │
                    ┌───────────────┐                     │
                    │ В РАБОТЕ      │──── изменение ──────┘
                    │ in_progress   │      суммы (>15%)
                    └───────┬───────┘      требует
                            │              согласования
                            ▼
                    ┌───────────────┐
                    │ ВЫПОЛНЕН      │
                    │ completed     │
                    └───────┬───────┘
                            │
               ┌────────────┴────────────┐
               ▼                         ▼
       ┌───────────────┐       ┌───────────────┐
       │ ОПЛАЧЕН       │       │ ОЖИДАЕТ       │
       │ paid          │       │ ОПЛАТЫ        │
       └───────┬───────┘       │ awaiting_pay  │
               │               └───────┬───────┘
               │                       │
               ▼                       ▼
       ┌───────────────┐       ┌───────────────┐
       │ ЗАКРЫТ        │       │ ОПЛАЧЕН       │
       │ closed        │       │ paid          │
       └───────────────┘       └───────┬───────┘
                                       │
                                       ▼
                               ┌───────────────┐
                               │ ЗАКРЫТ        │
                               │ closed        │
                               └───────────────┘

Параллельные состояния:
┌───────────────┐    ┌───────────────┐
│ ОТМЕНЁН       │    │ СПОР          │
│ cancelled     │    │ disputed      │
└───────────────┘    └───────────────┘
```

---

## 7. Безопасность и защита данных

### 7.1 Архитектура безопасности

```
┌─────────────────────────────────────────────────────────────────┐
│                    УРОВНИ БЕЗОПАСНОСТИ                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ УРОВЕНЬ 1: ПЕРИМЕТР                                             │
│ • WAF (Web Application Firewall)                                │
│ • DDoS Protection                                               │
│ • Rate Limiting                                                 │
│ • SSL/TLS шифрование                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ УРОВЕНЬ 2: АУТЕНТИФИКАЦИЯ                                       │
│ • JWT токены (access + refresh)                                 │
│ • OAuth 2.0 (Госуслуги, соц. сети)                              │
│ • 2FA (SMS, TOTP)                                               │
│ • Device fingerprinting                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ УРОВЕНЬ 3: АВТОРИЗАЦИЯ                                          │
│ • RBAC (Role-Based Access Control)                              │
│ • Проверка владения ресурсом                                    │
│ • Изоляция данных партнёров                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ УРОВЕНЬ 4: ДАННЫЕ                                               │
│ • Шифрование персональных данных (AES-256)                      │
│ • Маскирование (карты, телефоны)                                │
│ • Логирование доступа к ПДн                                     │
│ • Резервное копирование                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Защита от увода клиентов

```
┌─────────────────────────────────────────────────────────────────┐
│              МЕХАНИЗМЫ ЗАЩИТЫ ОТ УВОДА КЛИЕНТОВ                 │
└─────────────────────────────────────────────────────────────────┘

1. СКРЫТИЕ КОНТАКТОВ В ЧАТЕ
   ┌─────────────────────────────────────────────────────────────┐
   │ Сообщения проходят через фильтр:                           │
   │ • Телефоны: +7(XXX)XXX-XX-XX → [номер скрыт]              │
   │ • Email: xxx@xxx.xx → [email скрыт]                        │
   │ • Ссылки на соц.сети → [ссылка скрыта]                     │
   │ • Адреса вне контекста → [адрес скрыт]                     │
   └─────────────────────────────────────────────────────────────┘

2. ОТЛОЖЕННОЕ РАСКРЫТИЕ ЦЕН
   ┌─────────────────────────────────────────────────────────────┐
   │ AI/Эксперт подбор:                                         │
   │ • Этап 1: Название, артикул (БЕЗ ЦЕН)                      │
   │ • Этап 2: Кнопка "Показать предложения"                    │
   │ • Этап 3: Цены + продавцы (комиссия платформы)             │
   └─────────────────────────────────────────────────────────────┘

3. МОНИТОРИНГ ПОДОЗРИТЕЛЬНОЙ АКТИВНОСТИ
   ┌─────────────────────────────────────────────────────────────┐
   │ Триггеры:                                                   │
   │ • Множество запросов без покупок                           │
   │ • Попытки отправки контактов в чате                        │
   │ • Резкое падение конверсии у партнёра                      │
   │ Actions:                                                    │
   │ • Предупреждение партнёру                                  │
   │ • Временная блокировка                                      │
   │ • Штрафные санкции                                         │
   └─────────────────────────────────────────────────────────────┘
```

### 7.3 Роли и права доступа

| Роль | Права |
|------|-------|
| **Клиент** | Просмотр каталога, заказы, отзывы, свой профиль |
| **Партнёр** | Управление своими услугами/товарами, заказами, календарём |
| **Эксперт** | Очередь запросов, чат с клиентами, подбор запчастей |
| **Модератор** | Проверка партнёров, модерация отзывов, споры |
| **Администратор** | Полный доступ, настройки системы, финансы |
| **Суперадмин** | Управление ролями, критические операции |

---

## Приложения

### A. Структура базы данных (основные сущности)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     users       │     │    vehicles     │     │    partners     │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id              │     │ id              │     │ id              │
│ email           │     │ user_id    ────►│◄────│ user_id         │
│ phone           │     │ brand           │     │ name            │
│ password_hash   │     │ model           │     │ type            │
│ role            │     │ year            │     │ inn             │
│ created_at      │     │ vin             │     │ location        │
└─────────────────┘     │ engine_type     │     │ rating          │
                        └─────────────────┘     │ is_verified     │
                                                └─────────────────┘
                                                        │
                        ┌───────────────────────────────┘
                        │
┌─────────────────┐     │     ┌─────────────────┐
│    services     │     │     │    products     │
├─────────────────┤     │     ├─────────────────┤
│ id              │     │     │ id              │
│ name            │     │     │ name            │
│ category_id     │     │     │ article         │
│ description     │     │     │ category_id     │
│ base_price      │     │     │ description     │
└─────────────────┘     │     └─────────────────┘
        │               │               │
        │               │               │
        ▼               ▼               ▼
┌─────────────────────────────────────────────────────┐
│                      orders                         │
├─────────────────────────────────────────────────────┤
│ id                                                  │
│ client_id ─────────────────────────────────►users   │
│ partner_id ────────────────────────────────►partners│
│ vehicle_id ────────────────────────────────►vehicles│
│ order_type (service/product)                        │
│ status                                              │
│ estimated_amount                                    │
│ final_amount                                        │
│ scheduled_at                                        │
│ created_at                                          │
└─────────────────────────────────────────────────────┘
```

### B. API Endpoints (основные)

```
AUTH
  POST   /api/v1/auth/register
  POST   /api/v1/auth/login
  POST   /api/v1/auth/refresh
  POST   /api/v1/auth/logout

USERS
  GET    /api/v1/users/me
  PATCH  /api/v1/users/me
  
VEHICLES (Гараж)
  GET    /api/v1/vehicles
  POST   /api/v1/vehicles
  POST   /api/v1/vehicles/recognize    # OCR
  GET    /api/v1/vehicles/{id}
  PATCH  /api/v1/vehicles/{id}
  DELETE /api/v1/vehicles/{id}

CATALOG
  GET    /api/v1/services
  GET    /api/v1/services/{id}
  GET    /api/v1/products
  GET    /api/v1/products/{id}
  GET    /api/v1/categories

SEARCH
  POST   /api/v1/search/partners
  POST   /api/v1/search/services
  POST   /api/v1/search/products

BOOKING
  GET    /api/v1/partners/{id}/slots
  POST   /api/v1/slots/{id}/reserve
  POST   /api/v1/slots/{id}/confirm

ORDERS
  GET    /api/v1/orders
  POST   /api/v1/orders
  GET    /api/v1/orders/{id}
  PATCH  /api/v1/orders/{id}
  POST   /api/v1/orders/{id}/cancel

PAYMENTS
  POST   /api/v1/payments
  GET    /api/v1/payments/{id}
  POST   /api/v1/payments/webhook

EMERGENCY
  POST   /api/v1/emergency
  GET    /api/v1/emergency/{id}
  POST   /api/v1/emergency/{id}/accept    # для партнёров

AI PARTS
  POST   /api/v1/parts/recognize
  POST   /api/v1/parts/search
  GET    /api/v1/parts/{article}/offers

CHAT
  GET    /api/v1/chats
  POST   /api/v1/chats
  GET    /api/v1/chats/{id}/messages
  POST   /api/v1/chats/{id}/messages

REVIEWS
  GET    /api/v1/partners/{id}/reviews
  POST   /api/v1/orders/{id}/review

PARTNER PORTAL
  GET    /api/v1/partner/profile
  PATCH  /api/v1/partner/profile
  GET    /api/v1/partner/services
  POST   /api/v1/partner/services
  GET    /api/v1/partner/orders
  PATCH  /api/v1/partner/orders/{id}
  GET    /api/v1/partner/calendar
  PATCH  /api/v1/partner/calendar
  GET    /api/v1/partner/analytics
```

---

## Следующие шаги

1. **Фаза 1: MVP (Web-приложение на Python)**
   - Выбор стека: Reflex / FastAPI+React / Django
   - Базовая регистрация/авторизация
   - Гараж (ручной ввод авто)
   - Каталог услуг
   - Поиск партнёров на карте
   - Простое бронирование
   - Базовый ЛК партнёра

2. **Фаза 2: Расширение функционала**
   - OCR распознавание документов
   - Онлайн оплата
   - Уведомления (email, push)
   - Отзывы и рейтинги
   - Расширенный ЛК партнёра

3. **Фаза 3: AI и Экстренные услуги**
   - AI подбор запчастей
   - Чат с экспертами
   - Экстренная помощь
   - Эвакуатор, шиномонтаж

4. **Фаза 4: Мобильные приложения (v2.0)**
   - 📱 iOS приложение (Swift / React Native)
   - 📱 Android приложение (Kotlin / React Native)
   - Push-уведомления
   - Offline-режим

5. **Фаза 5: Масштабирование**
   - Интеграции с каталогами запчастей
   - Продвинутая аналитика
   - Маркетинговые инструменты
   - Программа лояльности

---

*Документ подготовлен на основе ТЗ v1.0 от 22.01.2026*

.PHONY: help install install-dev lint test test-cov migrate migrate-create \
        up down logs shell shell-db seed build clean

# ─── Переменные ───────────────────────────────────────────────────────────────
BACKEND_DIR  := backend
FRONTEND_DIR := frontend
DC           := docker compose -f infra/docker-compose.yml
DC_PROD      := docker compose -f infra/docker-compose.prod.yml
PYTHON       := python3

# ─── Помощь ───────────────────────────────────────────────────────────────────
help: ## Показать список команд
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Установка зависимостей ───────────────────────────────────────────────────
install: ## Установить prod-зависимости
	cd $(BACKEND_DIR) && pip install .

install-dev: ## Установить dev-зависимости
	cd $(BACKEND_DIR) && pip install -e ".[dev]"
	cd $(FRONTEND_DIR) && pip install -e ".[dev]"
	pre-commit install

# ─── Линтинг и форматирование ─────────────────────────────────────────────────
lint: ## Запустить ruff + mypy
	cd $(BACKEND_DIR) && ruff check . && ruff format --check . && mypy app

fmt: ## Форматировать код
	cd $(BACKEND_DIR) && ruff format . && ruff check --fix .

# ─── Тесты ────────────────────────────────────────────────────────────────────
test: ## Запустить тесты
	cd $(BACKEND_DIR) && pytest -x -q

test-cov: ## Тесты с покрытием
	cd $(BACKEND_DIR) && pytest --cov=app --cov-report=term-missing --cov-report=html -q

# ─── Миграции ─────────────────────────────────────────────────────────────────
migrate: ## Применить миграции
	cd $(BACKEND_DIR) && alembic upgrade head

migrate-create: ## Создать миграцию (передай: make migrate-create MSG="описание")
	cd $(BACKEND_DIR) && alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Откатить последнюю миграцию
	cd $(BACKEND_DIR) && alembic downgrade -1

# ─── Docker ───────────────────────────────────────────────────────────────────
up: ## Поднять dev-окружение
	$(DC) up -d

up-build: ## Пересобрать и поднять
	$(DC) up -d --build

down: ## Остановить окружение
	$(DC) down

down-v: ## Остановить и удалить volumes
	$(DC) down -v

logs: ## Логи всех контейнеров
	$(DC) logs -f

logs-api: ## Логи backend
	$(DC) logs -f api

ps: ## Статус контейнеров
	$(DC) ps

# ─── Shell ────────────────────────────────────────────────────────────────────
shell: ## Войти в контейнер backend
	$(DC) exec api bash

shell-db: ## psql в контейнере PostgreSQL
	$(DC) exec postgres psql -U $${POSTGRES_USER:-autohub} -d $${POSTGRES_DB:-autohub_db}

# ─── Seed ──────────────────────────────────────────────────────────────────────
seed: ## Заполнить БД тестовыми данными
	cd $(BACKEND_DIR) && $(PYTHON) -m app.scripts.seed

# ─── Сборка образов ───────────────────────────────────────────────────────────
build: ## Собрать Docker-образы
	$(DC) build

build-prod: ## Собрать prod-образы
	$(DC_PROD) build

# ─── Очистка ──────────────────────────────────────────────────────────────────
clean: ## Удалить кэш Python
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache"  -exec rm -rf {} + 2>/dev/null || true

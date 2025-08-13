# Makefile для Smart Cardiologist

.PHONY: help install install-dev setup-db migrate run test clean lint format

# Переменные
PYTHON = python3
PIP = pip3
VENV = venv
APP = src.main:app

help: ## Показать справку
	@echo "Smart Cardiologist - доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	$(PIP) install -r requirements.txt

install-dev: ## Установить зависимости для разработки
	$(PIP) install -r requirements.txt
	$(PIP) install black flake8 mypy pytest pytest-asyncio httpx

setup-db: ## Настроить базу данных PostgreSQL
	@echo "Настройка базы данных..."
	$(PYTHON) scripts/setup_database.py

migrate: ## Создать и применить миграции базы данных
	@echo "Создание миграции..."
	alembic revision --autogenerate -m "Auto migration"
	@echo "Применение миграции..."
	alembic upgrade head

migrate-init: ## Инициализировать Alembic (только при первом запуске)
	@echo "Инициализация Alembic..."
	alembic init migrations
	@echo "Alembic инициализирован. Отредактируйте migrations/env.py и запустите migrate"

run: ## Запустить приложение в режиме разработки
	@echo "Запуск приложения..."
	uvicorn $(APP) --reload --host 0.0.0.0 --port 8000

run-prod: ## Запустить приложение в продакшн режиме
	@echo "Запуск приложения в продакшн режиме..."
	uvicorn $(APP) --host 0.0.0.0 --port 8000

test: ## Запустить тесты
	@echo "Запуск тестов..."
	pytest tests/ -v

test-cov: ## Запустить тесты с покрытием
	@echo "Запуск тестов с покрытием..."
	pytest tests/ --cov=src --cov-report=html

lint: ## Проверить код линтером
	@echo "Проверка кода..."
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	mypy src/

format: ## Форматировать код
	@echo "Форматирование кода..."
	black src/ tests/ --line-length=88

format-check: ## Проверить форматирование кода
	@echo "Проверка форматирования..."
	black --check src/ tests/ --line-length=88

clean: ## Очистить временные файлы
	@echo "Очистка временных файлов..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

db-reset: ## Сбросить базу данных (ОСТОРОЖНО!)
	@echo "Сброс базы данных..."
	@read -p "Вы уверены? Это удалит все данные! [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		alembic downgrade base; \
		alembic upgrade head; \
		echo "База данных сброшена"; \
	else \
		echo "Операция отменена"; \
	fi

check-env: ## Проверить переменные окружения
	@echo "Проверка переменных окружения..."
	@if [ ! -f .env ]; then \
		echo "Файл .env не найден. Скопируйте env.example в .env и настройте"; \
		exit 1; \
	fi
	@echo "Файл .env найден"

health: ## Проверить здоровье приложения
	@echo "Проверка здоровья приложения..."
	curl -s http://localhost:8000/health | jq . || echo "Приложение не запущено"

setup: check-env install setup-db migrate ## Полная настройка проекта
	@echo "Проект настроен успешно!"

dev-setup: check-env install-dev setup-db migrate ## Настройка для разработки
	@echo "Проект настроен для разработки!"

# Команды для работы с базой данных
db-status: ## Показать статус миграций
	alembic current
	alembic history

db-upgrade: ## Обновить базу данных до последней версии
	alembic upgrade head

db-downgrade: ## Откатить последнюю миграцию
	alembic downgrade -1

# Команды для работы с API
api-test: ## Протестировать API endpoints
	@echo "Тестирование API..."
	$(PYTHON) scripts/test_api.py

# Команды для логирования
logs: ## Показать логи приложения
	@echo "Логи приложения (если настроено логирование в файлы)..."
	@if [ -f logs/app.log ]; then \
		tail -f logs/app.log; \
	else \
		echo "Файл логов не найден"; \
	fi

# Команды для мониторинга
monitor: ## Мониторинг системы
	@echo "Мониторинг системы..."
	@echo "Память:"
	free -h
	@echo "Диск:"
	df -h
	@echo "Процессы Python:"
	ps aux | grep python | grep -v grep || echo "Процессы Python не найдены"

# Команды для развертывания
deploy-check: ## Проверить готовность к развертыванию
	@echo "Проверка готовности к развертыванию..."
	@echo "1. Проверка зависимостей..."
	$(PIP) check
	@echo "2. Проверка тестов..."
	$(MAKE) test
	@echo "3. Проверка линтера..."
	$(MAKE) lint
	@echo "4. Проверка форматирования..."
	$(MAKE) format-check
	@echo "Все проверки пройдены успешно!"

# Справка по командам
commands: ## Показать все доступные команды
	@echo "Доступные команды:"
	@$(MAKE) help

# Команда по умолчанию
.DEFAULT_GOAL := help

.PHONY: help up down build logs clean test lint format

# Переменные
COMPOSE_FILE = docker-compose.yml
PROD_COMPOSE_FILE = docker-compose.prod.yml
PROJECT_NAME = suzy-lawyer

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Запустить приложение в режиме разработки
	docker compose -f $(COMPOSE_FILE) up --build

up-detached: ## Запустить приложение в фоновом режиме
	docker compose -f $(COMPOSE_FILE) up -d --build

down: ## Остановить приложение
	docker compose -f $(COMPOSE_FILE) down

down-prod: ## Остановить продакшн приложение
	docker compose -f $(PROD_COMPOSE_FILE) down

build: ## Собрать Docker образ
	docker compose -f $(COMPOSE_FILE) build

logs: ## Показать логи
	docker compose -f $(COMPOSE_FILE) logs -f

logs-api: ## Показать логи API
	docker compose -f $(COMPOSE_FILE) logs -f suzy-lawyer-api

logs-bot: ## Показать логи бота
	docker compose -f $(COMPOSE_FILE) logs -f suzy-lawyer-bot

clean: ## Очистить Docker ресурсы
	docker compose -f $(COMPOSE_FILE) down -v --rmi all
	docker system prune -f

up-prod: ## Запустить приложение в продакшн режиме
	docker compose -f $(PROD_COMPOSE_FILE) up -d --build

logs-prod: ## Показать продакшн логи
	docker compose -f $(PROD_COMPOSE_FILE) logs -f

test: ## Запустить тесты
	pytest src/tests/ -v

test-coverage: ## Запустить тесты с покрытием
	pytest src/tests/ --cov=src --cov-report=html

lint: ## Проверить код линтером
	flake8 src/ --max-line-length=120

format: ## Отформатировать код
	black src/

format-check: ## Проверить форматирование кода
	black src/ --check

type-check: ## Проверить типы
	mypy src/

security-check: ## Проверить безопасность
	bandit src/

install-dev: ## Установить зависимости для разработки
	pip install -r requirements.txt
	pip install pytest pytest-cov flake8 black mypy bandit

setup: ## Начальная настройка проекта
	@echo "Настройка проекта SuzyLawyer..."
	@if [ ! -f .env ]; then \
		echo "Создание .env файла из примера..."; \
		cp env.example .env; \
		echo "Пожалуйста, отредактируйте .env файл с вашими настройками"; \
	else \
		echo ".env файл уже существует"; \
	fi
	@echo "Установка зависимостей..."
	pip install -r requirements.txt
	@echo "Настройка завершена! Отредактируйте .env файл и запустите 'make up'"

health: ## Проверить здоровье сервисов
	@echo "Проверка API..."
	@curl -f http://localhost:8000/health || echo "API недоступен"
	@echo "Проверка контейнеров..."
	@docker compose -f $(COMPOSE_FILE) ps

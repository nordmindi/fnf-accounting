.PHONY: help setup install test lint format clean up down migrate upgrade downgrade run worker

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Setup development environment
	python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e .
	.venv/bin/pre-commit install
	cp env.example .env

install: ## Install dependencies
	pip install -r requirements.txt
	pip install -e .

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=src --cov-report=html --cov-report=term

lint: ## Run linting
	ruff check src tests
	mypy src
	bandit -r src
	pip-audit

format: ## Format code
	black src tests
	isort src tests
	ruff check --fix src tests

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf .ruff_cache

up: ## Start services with Docker Compose
	docker-compose up -d

down: ## Stop services
	docker-compose down

build: ## Build Docker images
	docker-compose build

logs: ## Show logs
	docker-compose logs -f

clean-docker: ## Clean Docker resources
	docker-compose down -v
	docker system prune -f

troubleshoot: ## Run Docker troubleshooting script
	./scripts/docker-troubleshoot.sh

setup-postman: ## Setup Postman collection for testing
	./scripts/setup-postman.sh

test-api: ## Test API endpoints with curl
	./scripts/test-api.sh

test-mvp: ## Test complete MVP pipeline functionality
	./scripts/test-mvp-pipeline.sh

test-fire-and-forget: ## Test Fire & Forget functionality with Swedish instructions
	./scripts/test-fire-and-forget.sh

demo: ## Demo the user experience - upload receipt with Swedish instruction
	./scripts/demo-user-experience.sh

test-bas: ## Test BAS compliance with Swedish accounting standards
	./scripts/test-bas-compliance.sh

test-booking-fix: ## Test the complete booking fix functionality
	./scripts/test-final-booking-fix.sh

test-content-type: ## Test content type handling fix
	./scripts/test-content-type-fix.sh

test-pipeline-booking: ## Test pipeline endpoint returns booking ID
	./scripts/test-pipeline-booking-id.sh

test-no-mock: ## Test entire flow with no mock data
	./scripts/test-no-mock-data.sh

toggle-mock: ## Toggle mock data on/off in .env file
	./scripts/toggle-mock-data.sh

migrate: ## Create new migration
	alembic revision --autogenerate -m "$(message)"

upgrade: ## Apply migrations
	alembic upgrade head

downgrade: ## Rollback migration
	alembic downgrade -1

setup-db: ## Setup database with migrations and BAS data
	./scripts/setup-database.sh

run: ## Run the application
	uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

worker: ## Run Celery worker
	celery -A src.orchestrator.celery_app worker --loglevel=info

dev: up setup-db run ## Start development environment

ci: lint test ## Run CI pipeline locally

ci-local: ## Run full CI pipeline locally with detailed output
	./scripts/test-ci-locally.sh
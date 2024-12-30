.PHONY: help install update test coverage lint format check docs

# Default target
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Set up the poetry environment
	@poetry install

update: ## Update the poetry environment
	@poetry update

test: ## Run tests
ifeq ($(OS),Windows_NT)
	@Start-Process -FilePath "vault" -ArgumentList "server", "-dev", "-dev-root-token-id=root", "-address=http://127.0.0.1:8200" -NoNewWindow -PassThru
	@poetry run pytest
	@taskkill /IM "vault.exe" /F
else
	@vault server -dev -dev-root-token-id="root" -address="http://127.0.0.1:8200" > /dev/null 2>&1 & echo $$! > vault_pid
	@poetry run pytest
	@if [ -f vault_pid ] && kill -0 `cat vault_pid` 2>/dev/null; then \
		kill -9 `cat vault_pid`; \
	fi
	@rm -f vault_pid
endif

coverage: ## Run tests with coverage
ifeq ($(OS),Windows_NT)
	@Start-Process -FilePath "vault" -ArgumentList "server", "-dev", "-dev-root-token-id=root", "-address=http://127.0.0.1:8200" -NoNewWindow -PassThru
	@poetry run pytest --cov=rxconf --cov-report=xml --cov-report=term
	@taskkill /IM "vault.exe" /F
else
	@vault server -dev -dev-root-token-id="root" -address="http://127.0.0.1:8200" > /dev/null 2>&1 & echo $$! > vault_pid
	@poetry run pytest --cov=rxconf --cov-report=xml --cov-report=term
	@if [ -f vault_pid ] && kill -0 `cat vault_pid` 2>/dev/null; then \
		kill -9 `cat vault_pid`; \
	fi
	@rm -f vault_pid
endif

format: ## Format sources
	@poetry run black .
	@poetry run isort .
	@poetry run ruff check . --fix

lint: ## Run linters
	@poetry run pyright .
	@poetry run ruff check .
	@poetry run mypy .
	@poetry run black --check .
	@poetry run isort --check .

check: lint coverage ## Run linters & tests

docs: ## Build and serve documentation with mkdocs
	@poetry run mkdocs serve

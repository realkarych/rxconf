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
	@kill -9 `cat vault_pid` && rm -f vault_pid
endif

coverage: ## Run tests with coverage
ifeq ($(OS),Windows_NT)
	@Start-Process -FilePath "vault" -ArgumentList "server", "-dev", "-dev-root-token-id=root", "-address=http://127.0.0.1:8200" -NoNewWindow -PassThru
	@poetry run pytest --cov=rxconf --cov-report=xml --cov-report=term
	@taskkill /IM "vault.exe" /F
else
	@vault server -dev -dev-root-token-id="root" -address="http://127.0.0.1:8200" > /dev/null 2>&1 & echo $$! > vault_pid
	@poetry run pytest --cov=rxconf --cov-report=xml --cov-report=term
	@kill -9 `cat vault_pid` && rm -f vault_pid
endif

format: ## Format sources
	@poetry run black .
	@poetry run isort .
	@poetry run ruff check . --fix

lint: ## Run linters (pyright, ruff, mypy)
	@poetry run pyright .
	@poetry run ruff check .
	@poetry run mypy .

check: lint coverage  ## Run linters & tests

docs: ## Build and serve documentation with mkdocs
	@poetry run mkdocs serve

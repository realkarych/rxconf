.PHONY: help install update test lint test-lint docs

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
	@poetry shell
	@poetry run pytest

lint: ## Run linters (pyright, ruff, flake8, mypy)
	@poetry shell
	@poetry run pyright .
	@poetry run ruff check .
	@poetry run flake8
	@poetry run mypy .

test-lint: test lint ## Run tests and linters

docs: ## Build and serve documentation with mkdocs
	@poetry run mkdocs serve

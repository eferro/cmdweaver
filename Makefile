.PHONY: help local-setup build update test test-unit test-coverage clean

.DEFAULT_GOAL := help

PACKAGE_NAME = cmdweaver

help: ## Show this help
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

local-setup: ## Sets up the local environment (install dependencies)
	pip install -e .
	pip install -r requirements-dev.txt
	@echo "✅ Local environment setup complete"

build: ## Builds the package
	pip install build
	python -m build

update: ## Updates the app packages
	pip install --upgrade pip
	pip install -e .
	pip install -r requirements-dev.txt

test: test-unit ## Run all tests (pytest)

test-unit: ## Run unit tests with pytest
	pytest tests/unit -v

test-coverage: ## Run tests with coverage report
	pytest tests/unit --cov=$(PACKAGE_NAME) --cov-report=term-missing --cov-report=html

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned!"

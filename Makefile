.PHONY: help local-setup build update test test-coverage clean

.DEFAULT_GOAL := help

PACKAGE_NAME = boscli
SPEC_DIR = spec

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

test: ## Run all tests
	mamba $(SPEC_DIR)

test-coverage: ## Run tests with coverage report
	coverage run --source=$(PACKAGE_NAME) -m mamba $(SPEC_DIR)
	coverage report -m
	coverage html

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned!"

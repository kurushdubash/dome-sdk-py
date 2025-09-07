.PHONY: help install install-dev test test-cov lint format type-check clean build publish

# Default target
help:
	@echo "Available targets:"
	@echo "  install      Install package in development mode"
	@echo "  install-dev  Install package with development dependencies"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage"
	@echo "  lint         Run linting (flake8)"
	@echo "  format       Format code (black, isort)"
	@echo "  type-check   Run type checking (mypy)"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build package"
	@echo "  publish      Publish package to PyPI"
	@echo "  dev-setup    Set up development environment"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Development setup
dev-setup: install-dev
	pre-commit install

# Testing
test:
	pytest

test-cov:
	pytest --cov=dome_api_sdk --cov-report=term-missing --cov-report=html

# Linting and formatting
lint:
	flake8 src tests

format:
	black src tests
	isort src tests

format-check:
	black --check src tests
	isort --check-only src tests

# Type checking
type-check:
	mypy src

# Quality checks (run all)
quality: format-check lint type-check test

# Building and publishing
clean:
	rm -rf build dist *.egg-info
	rm -rf htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish: build
	python -m twine upload dist/*

# Development helpers
dev-install: dev-setup
	@echo "Development environment set up successfully!"

pre-commit:
	pre-commit run --all-files

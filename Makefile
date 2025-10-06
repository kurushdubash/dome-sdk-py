.PHONY: help install install-dev test test-cov lint format type-check clean build publish release test-release

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
	@echo "  release      Full release process (clean, validate, build, publish)"
	@echo "  test-release Full release process to Test PyPI"
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

# Release process - comprehensive validation and publishing
release:
	@echo "🚀 Starting release process..."
	@echo "=================================="
	@echo "1. Validating Git state..."
	@# Check if we're on main branch
	@if [ "$$(git branch --show-current)" != "main" ]; then \
		echo "❌ Error: Must be on main branch. Current branch: $$(git branch --show-current)"; \
		exit 1; \
	fi
	@echo "✅ On main branch"
	@# Check if there are uncommitted changes
	@if ! git diff-index --quiet HEAD --; then \
		echo "❌ Error: Uncommitted changes detected. Please commit or stash them first."; \
		git status --porcelain; \
		exit 1; \
	fi
	@echo "✅ No uncommitted changes"
	@# Check if there are stashed changes
	@if [ -n "$$(git stash list)" ]; then \
		echo "❌ Error: Stashed changes detected. Please apply or drop them first."; \
		git stash list; \
		exit 1; \
	fi
	@echo "✅ No stashed changes"
	@# Check if we're at head of remote
	@git fetch origin
	@if [ "$$(git rev-parse HEAD)" != "$$(git rev-parse origin/main)" ]; then \
		echo "❌ Error: Local main is not at head of remote main."; \
		echo "Local:  $$(git rev-parse HEAD)"; \
		echo "Remote: $$(git rev-parse origin/main)"; \
		echo "Please pull the latest changes first."; \
		exit 1; \
	fi
	@echo "✅ At head of remote main"
	@echo ""
	@echo "2. Running quality checks..."
	@$(MAKE) quality
	@echo ""
	@echo "3. Cleaning and building..."
	@$(MAKE) clean
	@$(MAKE) build
	@echo ""
	@echo "4. Package built successfully!"
	@echo "Files ready for upload:"
	@ls -la dist/
	@echo ""
	@echo "5. Publishing to PyPI..."
	@echo "⚠️  This will upload to the real PyPI. Press Ctrl+C to cancel within 5 seconds..."
	@sleep 5
	@$(MAKE) publish
	@echo ""
	@echo "🎉 Release completed successfully!"
	@echo "Package version: $$(python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"

# Test release process - same as release but uploads to Test PyPI
test-release:
	@echo "🧪 Starting test release process..."
	@echo "=================================="
	@echo "1. Validating Git state..."
	@# Check if we're on main branch
	@if [ "$$(git branch --show-current)" != "main" ]; then \
		echo "❌ Error: Must be on main branch. Current branch: $$(git branch --show-current)"; \
		exit 1; \
	fi
	@echo "✅ On main branch"
	@# Check if there are uncommitted changes
	@if ! git diff-index --quiet HEAD --; then \
		echo "❌ Error: Uncommitted changes detected. Please commit or stash them first."; \
		git status --porcelain; \
		exit 1; \
	fi
	@echo "✅ No uncommitted changes"
	@# Check if there are stashed changes
	@if [ -n "$$(git stash list)" ]; then \
		echo "❌ Error: Stashed changes detected. Please apply or drop them first."; \
		git stash list; \
		exit 1; \
	fi
	@echo "✅ No stashed changes"
	@# Check if we're at head of remote
	@git fetch origin
	@if [ "$$(git rev-parse HEAD)" != "$$(git rev-parse origin/main)" ]; then \
		echo "❌ Error: Local main is not at head of remote main."; \
		echo "Local:  $$(git rev-parse HEAD)"; \
		echo "Remote: $$(git rev-parse origin/main)"; \
		echo "Please pull the latest changes first."; \
		exit 1; \
	fi
	@echo "✅ At head of remote main"
	@echo ""
	@echo "2. Running quality checks..."
	@$(MAKE) quality
	@echo ""
	@echo "3. Cleaning and building..."
	@$(MAKE) clean
	@$(MAKE) build
	@echo ""
	@echo "4. Package built successfully!"
	@echo "Files ready for upload:"
	@ls -la dist/
	@echo ""
	@echo "5. Publishing to Test PyPI..."
	@echo "⚠️  This will upload to Test PyPI. Press Ctrl+C to cancel within 3 seconds..."
	@sleep 3
	@python -m twine upload --repository testpypi dist/*
	@echo ""
	@echo "🎉 Test release completed successfully!"
	@echo "Package version: $$(python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"
	@echo "Test PyPI URL: https://test.pypi.org/project/dome-api-sdk/"

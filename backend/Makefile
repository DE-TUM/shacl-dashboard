# Makefile for SHACL Dashboard Backend
# Provides convenient commands for development tasks

.PHONY: help install install-dev test coverage lint format security check clean run

# Default target
help:
	@echo "SHACL Dashboard Backend - Available Commands:"
	@echo ""
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make test          - Run tests with pytest"
	@echo "  make coverage      - Run tests with coverage report"
	@echo "  make lint          - Run all linters (pylint, flake8, mypy)"
	@echo "  make format        - Format code with black and isort"
	@echo "  make security      - Run security scan with bandit"
	@echo "  make check         - Run all quality checks (format, lint, security, test)"
	@echo "  make complexity    - Analyze code complexity with radon"
	@echo "  make clean         - Remove temporary files and caches"
	@echo "  make run           - Run the Flask application"
	@echo ""

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements-dev.txt
	pip install pre-commit
	pre-commit install

# Run tests
test:
	python -m pytest tests/ -v

# Run tests with coverage report
coverage:
	python -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html --cov-report=xml
	@echo ""
	@echo "Coverage HTML report generated in htmlcov/index.html"

# Run linters
lint:
	@echo "Running pylint..."
	python -m pylint **/*.py --rcfile=.pylintrc || true
	@echo ""
	@echo "Running flake8..."
	python -m flake8 . --max-line-length=120 --extend-ignore=E203,W503 || true
	@echo ""
	@echo "Running mypy..."
	python -m mypy . --config-file=pyproject.toml || true

# Format code
format:
	@echo "Formatting with black..."
	python -m black . --line-length=120
	@echo ""
	@echo "Organizing imports with isort..."
	python -m isort . --profile=black --line-length=120

# Security scan
security:
	@echo "Running bandit security scan..."
	python -m bandit -r . -c pyproject.toml || true

# Code complexity analysis
complexity:
	@echo "Analyzing code complexity with radon..."
	@echo ""
	@echo "=== Cyclomatic Complexity ==="
	python -m radon cc . -a -s
	@echo ""
	@echo "=== Maintainability Index ==="
	python -m radon mi . -s

# Run all quality checks
check: format lint security test
	@echo ""
	@echo "All quality checks completed!"

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml 2>/dev/null || true
	@echo "Clean complete!"

# Run Flask application
run:
	python app.py

# Install pre-commit hooks
setup-hooks:
	pip install pre-commit
	pre-commit install
	@echo "Pre-commit hooks installed successfully!"

# Run pre-commit on all files
pre-commit:
	pre-commit run --all-files

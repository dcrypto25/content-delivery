# TrainerApp.AI - Content Automation Makefile

.PHONY: help install test run deploy clean

help:
	@echo "TrainerApp.AI Content Automation System"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       - Install Python dependencies"
	@echo "  make test          - Run tests"
	@echo "  make generate      - Generate test batch (10 posts)"
	@echo "  make generate-full - Generate full batch (100 posts)"
	@echo "  make deploy        - Deploy with Docker"
	@echo "  make stop          - Stop Docker containers"
	@echo "  make logs          - View logs"
	@echo "  make analytics     - Collect analytics"
	@echo "  make clean         - Clean generated files"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

test:
	@echo "Running tests..."
	python scripts/generators/prompt_generator.py --theme workout --quantity 3
	@echo "✓ Tests passed"

generate:
	@echo "Generating test batch (10 posts, no posting)..."
	python scripts/orchestrator.py --theme workout --quantity 10 --skip-posting

generate-full:
	@echo "Generating full batch (100 posts)..."
	python scripts/orchestrator.py --theme workout --quantity 100

deploy:
	@echo "Deploying with Docker..."
	docker-compose up -d
	@echo "✓ Deployed! Access n8n at http://localhost:5678"

stop:
	@echo "Stopping containers..."
	docker-compose down

logs:
	docker-compose logs -f content-generator

analytics:
	@echo "Collecting analytics..."
	python scripts/analytics/collect_metrics.py

clean:
	@echo "Cleaning generated files..."
	rm -rf storage/generated/images/*
	rm -rf storage/generated/videos/*
	rm -rf storage/generated/temp/*
	rm -rf logs/*.log
	@echo "✓ Cleaned"

setup-env:
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Created .env file - Please edit with your API keys"; \
	else \
		echo ".env already exists"; \
	fi

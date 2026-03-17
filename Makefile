# Makefile for SMARAN System

.PHONY: install seed run test run-docker all clean check-env

PYTHON = python
PIP = pip
UVICORN = uvicorn
STREAMLIT = streamlit

all: install check-env test run

install:
	@echo "📦 Installing Dependencies..."
	$(PIP) install -r requirements.txt

check-env:
	@echo "🔍 Checking Environment Variables..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Copying .env.example -> .env"; \
		cp .env.example .env; \
		echo "⚠️ PLEASE FILL OUT .env BEFORE CONTINUING."; \
		exit 1; \
	fi

run:
	@echo "🚀 Launching Full System locally using Bash sequence..."
	bash start.sh

run-docker:
	@echo "🐳 Launching via Docker Compose..."
	docker-compose up --build

run-api:
	@echo "⚡ Starting FastAPI alone..."
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000 --reload

clean:
	@echo "🧹 Cleaning up temp files and __pycache__..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test:
	@echo "🧪 Running Pytest Coverage Suite..."
	export PYTHONPATH=$$(pwd) && pytest tests/ -v

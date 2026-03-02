# Makefile for SMARAN System

.PHONY: install seed run test run-docker all clean check-env

PYTHON = python
PIP = pip
UVICORN = uvicorn
STREAMLIT = streamlit

all: install check-env seed test run

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

seed:
	@echo "🌱 Initializing Graph and Seeding Data..."
	export PYTHONPATH=$$(pwd) && $(PYTHON) app/graph/init_graph.py
	@# Requires API to be running for proper seed ingestion structure
	@echo "⚠️ Seed requires API to be running on port 8000. Use 'sh start.sh' for sequence execution."

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

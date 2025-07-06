# === GitHub Anomaly Detection Project: Makefile ===

# --------- Configuration ---------
PIPENV := pipenv run
DOCKER_IMAGE := github-anomaly-inference
DOCKERFILE := Dockerfile.inference
PORT := 8000

# --------- Help ---------

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Code Quality:"
	@echo "  format         Format code using Black"
	@echo "  lint           Lint code using Flake8"
	@echo "  test           Run tests using pytest"
	@echo "  check          Run format, lint, and test together"
	@echo ""
	@echo "Docker & FastAPI:"
	@echo "  docker-build   Build Docker image for FastAPI"
	@echo "  docker-run     Run FastAPI container"
	@echo "  api-test       Send test POST request to API"
	@echo ""
	@echo "Airflow:"
	@echo "  airflow-up     Start Airflow core services"
	@echo "  airflow-down   Stop all Airflow services"
	@echo ""
	@echo "Setup & Cleanup:"
	@echo "  install        Install all dependencies via Pipenv"
	@echo "  clean          Remove __pycache__ and .pyc files"

# --------- Setup ---------

install:
	pipenv install --dev

# --------- Code Quality ---------

format:
	$(PIPENV) black .

lint:
	$(PIPENV) flake8 .

test:
	$(PIPENV) pytest

check: format lint test

# --------- Docker & FastAPI ---------

docker-build:
	docker build -t $(DOCKER_IMAGE) -f $(DOCKERFILE) .

docker-run:
	docker run -p $(PORT):$(PORT) $(DOCKER_IMAGE)

api-test:
	curl -X POST http://localhost:$(PORT)/predict \
	     -H "Content-Type: application/json" \
	     -d '{"features": [12, 0, 1, 0, 4]}'

# --------- Airflow ---------

airflow-up:
	docker compose up --build

airflow-down:
	docker compose down

# --------- Utility ---------

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -delete

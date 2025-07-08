# === GitHub Anomaly Detection Project: Makefile ===

# === Guards ===

check-terraform:
	@command -v terraform >/dev/null 2>&1 || \
	{ echo >&2 "❌ Terraform is not installed. Run 'make install-terraform' first."; 

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
	@echo "Terraform:"
	@echo "  install-terraform  Install Terraform CLI if not present"
	@echo "  terraform-init         Initialize Terraform config"
	@echo "  terraform-apply        Provision MLflow container (port 5050)"
	@echo "  terraform-destroy      Tear down MLflow container"
	@echo "  terraform-status       Show current infra state"
	@echo ""
	@echo "Setup & Cleanup:"
	@echo "  install        Install all dependencies via Pipenv"
	@echo "  create-env     Create .env file with required AIRFLOW_UID and alert config placeholders"
	@echo "  clean          Remove __pycache__ and .pyc files"

# --------- Setup ---------

install:
	pipenv install --dev

create-env:
	@if [ -f .env ]; then \
		echo "✅ .env file already exists. Skipping creation."; \
	else \
		echo "🔧 Creating .env template file..."; \
		echo "AIRFLOW_UID=50000" > .env; \
		echo "# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ" >> .env; \
		echo "# ALERT_EMAIL_FROM=your_email@example.com" >> .env; \
		echo "# ALERT_EMAIL_TO=recipient@example.com" >> .env; \
		echo "# ALERT_EMAIL_PASSWORD=your_app_password" >> .env; \
		echo "# ALERT_EMAIL_SMTP=smtp.gmail.com" >> .env; \
		echo "# ALERT_EMAIL_PORT=587" >> .env; \
		echo "✅ .env file created."; \
	fi

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

# --------- Terraform IaC for MLflow ---------

install-terraform:
	@command -v terraform >/dev/null 2>&1 && \
	{ echo "✅ Terraform is already installed."; } || \
	{ echo "⬇️ Installing Terraform..."; \
	curl -LO https://releases.hashicorp.com/terraform/1.8.2/terraform_1.8.2_linux_amd64.zip && \
	unzip -o terraform_1.8.2_linux_amd64.zip && \
	sudo mv terraform /usr/local/bin/ && \
	rm terraform_1.8.2_linux_amd64.zip && \
	echo "✅ Terraform installed successfully."; \
	terraform -version; }

terraform-init: check-terraform
	cd infra && terraform init

terraform-apply: check-terraform
	cd infra && terraform apply

terraform-destroy: check-terraform
	cd infra && terraform destroy

terraform-status: check-terraform
	cd infra && terraform show

# --------- Utility ---------

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -name "*.pyc" -delete

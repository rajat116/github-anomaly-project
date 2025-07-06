# ☁️ Infrastructure as Code (IaC): MLflow Server with Terraform

This Terraform module provisions a **Docker-based MLflow tracking server**, matching the setup used in `docker-compose.yaml`, but on a **different port (5050)** to avoid conflicts.

---

## 📁 Directory Structure

- infra/main.tf # Terraform configuration
- README.md # This file

## ⚙️ Requirements

- [Terraform](https://developer.hashicorp.com/terraform/downloads)
- [Docker](https://docs.docker.com/get-docker/)

## 🚀 How to Use

### 1. Navigate to the `infra/` folder

```bash
cd infra
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Apply the infrastructure

```bash
terraform apply # Confirm with yes when prompted.
```

### 4. 🔎 Verify

MLflow server will be available at:

```bash
http://localhost:5050
```

All artifacts will be stored in your project’s mlruns/ directory.

### 5. ❌ To Clean Up

```bash
terraform destroy
```

This removes the MLflow container provisioned by Terraform.


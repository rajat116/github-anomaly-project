# infra/main.tf

terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

# Use the same MLflow image as in docker-compose
resource "docker_image" "mlflow" {
  name = "ghcr.io/mlflow/mlflow:latest"
}

# MLflow container provisioned on port 5050
resource "docker_container" "mlflow_server" {
  name  = "mlflow-server-terraform"
  image = docker_image.mlflow.name

  ports {
    internal = 5000
    external = 5050
  }

  volumes {
    host_path      = "${path.cwd}/../mlruns"
    container_path = "/mlruns"
  }

  env = [
    "MLFLOW_BACKEND_STORE_URI=sqlite:///mlruns/mlflow.db",
    "MLFLOW_DEFAULT_ARTIFACT_ROOT=/mlruns/artifacts"
  ]

  command = [
    "mlflow", "server",
    "--backend-store-uri", "sqlite:///mlruns/mlflow.db",
    "--default-artifact-root", "/mlruns/artifacts",
    "--host", "0.0.0.0",
    "--port", "5000"
  ]
}
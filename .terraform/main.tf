locals {
  project    = var.project
  image      = var.image
  location   = var.location
  cloud_zone = var.cloud_zone

  service_name = "reech-matching-engine-api"
}

# ====================================================
# Specify Providers
provider "google" {
  project = local.project
  region  = local.location
  zone    = local.cloud_zone
}

# ====================================================
# Enable Google APIs
resource "google_project_service" "reech_ml_run_api" {
  service            = "run.googleapis.com"
  disable_on_destroy = true
}

resource "google_project_service" "reech_ml_resource_manager_api" {
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = true
}

resource "google_project_service" "reech_ml_container_registry_api" {
  service            = "containerregistry.googleapis.com"
  disable_on_destroy = true
}

resource "google_project_service" "reech_ml_iam_api" {
  service            = "iam.googleapis.com"
  disable_on_destroy = true
}

# ====================================================
# Create the Cloud Run service
resource "google_cloud_run_service" "cloud_run_service_b" {
  name     = local.service_name
  location = local.location

  template {
    spec {
      containers {
        image = local.image
      }
      service_account_name = google_service_account.cloud_run_ml_deployer_acc.email
    }
  }
  traffic {
    percent         = 100
    latest_revision = true
  }

  # Wait for the APIs to be enabled
  depends_on = [
    google_project_service.reech_ml_run_api,
    google_project_service.reech_ml_resource_manager_api,
    google_service_account.cloud_run_ml_deployer_acc
  ]
}

# ====================================================
# Create a Service Account for deployment
resource "google_service_account" "cloud_run_ml_deployer_acc" {
  project      = local.project
  account_id   = "reech-python-deployer-id02"
  display_name = "Deployment Service Account"
}

resource "google_service_account_key" "cloud_run_ml_deployer_acc_key" {
  service_account_id = google_service_account.cloud_run_ml_deployer_acc.name
}

resource "google_project_iam_member" "project_editor_iam_policy_001" {
  project = local.project
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.cloud_run_ml_deployer_acc.email}"
}

resource "google_cloud_run_service_iam_member" "cloud_run_svc_invoker_policy_1" {
  project  = local.project
  service  = google_cloud_run_service.cloud_run_service_b.name
  location = google_cloud_run_service.cloud_run_service_b.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}


# ====================================================
# Outputs

output "url" {
  value = google_cloud_run_service.cloud_run_service_b.status[0].url
}

output "cloud_run_ml_deployer_acc_key" {
  sensitive = true
  value     = base64decode(google_service_account_key.cloud_run_ml_deployer_acc_key.private_key)
}

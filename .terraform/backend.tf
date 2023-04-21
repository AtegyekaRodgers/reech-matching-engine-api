terraform {
  required_version = ">= 0.14"

  backend "gcs" {
    bucket = "reech-tfstate-storage-bucket"
    prefix = "matching_engine"
  }

  required_providers {
    # Cloud Run support was added on 3.3.0
    google = ">= 3.3"
  }

}

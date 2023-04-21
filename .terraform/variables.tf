variable "project" {
  type = string
}

variable "image" {
  type = string
}

variable "location" {
  type    = string
  default = "us-central1"
}

variable "cloud_zone" {
  type    = string
  default = "us-central1-c"
}

terraform {
  backend "gcs" {
    bucket = "terraform-state-attila-szombati"
  }
}
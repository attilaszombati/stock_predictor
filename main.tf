provider "google" {
  project = "attila-szombati-sandbox"
  region  = "us-central1"
}

resource "google_storage_bucket" "twitter-scraper-bucket" {
  name     = "twitter-scraper-data"
  location = "US-CENTRAL1"
}
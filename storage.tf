resource "google_storage_bucket" "twitter_data_collection" {
  name     = "twitter_data_collection"
  location = "us-central1"

  storage_class = "REGIONAL"

}

resource "google_storage_bucket" "crypto_data_collection" {
  name     = "crypto_data_collection"
  location = "us-central1"

  storage_class = "REGIONAL"

}

resource "google_storage_bucket" "stock_data_collection" {
  name     = "stock_data_collection"
  location = "us-central1"

  storage_class = "REGIONAL"

}

resource "google_storage_bucket" "stock_predictor_bucket" {
  name     = "stock_predictor_bucket"
  location = "us-central1"

  storage_class = "REGIONAL"

}

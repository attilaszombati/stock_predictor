resource "google_storage_bucket" "twitter_data_collection" {
  name     = "twitter_data_collection"
  location = "us-central1"

  storage_class = "REGIONAL"

}

resource "google_storage_bucket" "alpaca_data_collection" {
  name     = "alpaca_data_collection"
  location = "us-central1"

  storage_class = "REGIONAL"

}

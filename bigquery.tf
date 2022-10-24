resource "google_bigquery_dataset" "raw_layer" {
  dataset_id    = "raw_layer_tf"
  friendly_name = "Data warehouse raw layer"
  description   = "This is the raw layer of the data warehouse, where all the data is stored in its original form."
  location      = "us-central1"
}

resource "google_bigquery_dataset" "dl_layer" {
  dataset_id    = "dl_layer_tf"
  friendly_name = "Data warehouse deduplicated layer"
  description   = "This is the deduplicated layer of the data warehouse, where the duplicate data is removed."
  location      = "us-central1"
}

resource "google_bigquery_dataset" "cl_layer" {
  dataset_id    = "cl_layer_tf"
  friendly_name = "Data warehouse curated layer"
  description   = "This is the deduplicated layer of the data warehouse, where the business logic is applied. This is the layer that is used for creating AI models."
  location      = "us-central1"
}


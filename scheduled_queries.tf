resource "google_bigquery_table" "elon_musk_twitter_data" {
  dataset_id = google_bigquery_dataset.cl_layer.dataset_id
  table_id   = "elon_musk"

  external_data_configuration {
    autodetect    = true
    source_format = "PARQUET"

    source_uris = [
      "${google_storage_bucket.twitter_data_collection.url}/elon_musk/*.pq"
    ]
  }
}

resource "google_bigquery_table" "doge_usd_data" {
  dataset_id = google_bigquery_dataset.cl_layer.dataset_id
  table_id   = "doge_usd"

  external_data_configuration {
    autodetect    = true
    source_format = "PARQUET"

    source_uris = [
      "${google_storage_bucket.alpaca_data_collection.url}/DOGEUSD/*.pq"
    ]
  }
}

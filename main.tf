provider "google" {
  project = "attila-szombati-sandbox"
  region  = "us-central1"
}

resource "google_storage_bucket" "twitter-scraper-bucket" {
  name     = "twitter-scraper-data"
  location = "US-CENTRAL1"
}

data "archive_file" "function_zip" {
  type        = "zip"
  source_dir  = "${path.root}/cloud_function/"
  output_path = "${path.root}/cloud_function.zip"
}

resource "google_storage_bucket" "cloud_function_bucket" {
  name     = "twitter_scraper_bucket"
  location = "US-CENTRAL1"
}

# place the zip-ed code in the bucket
resource "google_storage_bucket_object" "hello_world_zip" {
  name   = "twitter_scraper"
  bucket = "${google_storage_bucket.cloud_function_bucket.name}"
  source = "${path.root}/cloud_function.zip"
}

resource "google_cloudfunctions_function" "twitter_scraper_function" {
  name                  = "twitter-scraper"
  available_memory_mb   = 512
  source_archive_bucket = "${google_storage_bucket.cloud_function_bucket.name}"
  source_archive_object = "${google_storage_bucket_object.hello_world_zip.name}"
  timeout               = 540
  entry_point           = "handler"
  trigger_http          = true
  runtime               = "python39"
}
terraform {
  backend "gcs" {
    bucket = "twitter_scraped_data"
    prefix = "terraform/state"
  }
}
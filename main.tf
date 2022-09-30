provider "google" {
  project = "attila-szombati-sandbox"
  region  = "us-central1"
}

resource "google_cloud_run_service" "twitter-scraper" {
  name     = "twitter-scraper"
  location = "us-central1"

  template {
    spec {
      containers {
        image = "gcr.io/attila-szombati-sandbox/twitter-scraper:latest"
        ports {
          container_port = 8080
        }
      }
      timeout_seconds      = 540
      service_account_name = google_service_account.storage-admin.email
    }
  }
  traffic {
    percent         = 100
    latest_revision = true
  }
  autogenerate_revision_name = true
}

resource "google_cloud_run_service" "crypto-data-scraper" {
  name     = "crypto-data-scraper"
  location = "us-central1"

  template {
    spec {
      containers {
        image = "gcr.io/attila-szombati-sandbox/crypto-data-scraper:latest"
        ports {
          container_port = 8080
        }
      }
      timeout_seconds      = 540
      service_account_name = google_service_account.storage-admin.email
    }
  }
  traffic {
    percent         = 100
    latest_revision = true
  }
  autogenerate_revision_name = true
}


resource "google_cloud_scheduler_job" "cloudrun-scheduler" {
  name             = "cloudrun-scheduler"
  description      = "Invoke cloud run"
  schedule         = "30 9 1-31/7 * *"
  time_zone        = "Europe/Budapest"
  attempt_deadline = "320s"

  retry_config {
    retry_count = 1
  }


  http_target {
    http_method = "POST"
    uri         = google_cloud_run_service.twitter-scraper.status.0.url
    headers     = { "Content-Type" : "application/json", "User-Agent" : "Google-Cloud-Scheduler" }
    body        = base64encode("{\"TWITTER_USERS\": [\"elonmusk\", \"JeffBezos\", \"BarackObama\", \"JoeBiden\", \"KamalaHarris\"], \"SCRAPING_TYPE\": \"news\"}")
    oidc_token {
      service_account_email = google_service_account.cloudrun-invoker.email
    }
  }
}

resource "google_cloud_scheduler_job" "crypto-data-scraper-scheduler" {
  name             = "crypto-data-scraper-scheduler"
  description      = "Invoke cloud run"
  schedule         = "1 * 5 1 *"
  time_zone        = "Europe/Budapest"
  attempt_deadline = "320s"

  retry_config {
    retry_count = 1
  }


  http_target {
    http_method = "POST"
    uri         = google_cloud_run_service.crypto-data-scraper.status.0.url
    headers     = { "Content-Type" : "application/json", "User-Agent" : "Google-Cloud-Scheduler" }
    body        = base64encode("{\"SYMBOLS\": [\"BTC-USD\"], \"SCRAPING_TYPE\": \"history\"}")
    oidc_token {
      service_account_email = google_service_account.cloudrun-invoker.email
    }
  }
}

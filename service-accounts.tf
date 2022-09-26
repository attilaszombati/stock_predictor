resource "google_service_account" "cloudrun-invoker" {
  account_id   = "cloudrun-invoker"
  display_name = "SA for invoke cloud run services"
}

resource "google_service_account" "crypto-data-scraper-invoker" {
  account_id   = "crypto-data-scraper-invoker"
  display_name = "SA for invoke cloud run services"
}

resource "google_cloud_run_service_iam_binding" "binding" {
  location = google_cloud_run_service.crypto-data-scraper.location
  service  = google_cloud_run_service.crypto-data-scraper.name
  role     = "roles/run.invoker"
  members = [
    "serviceAccount:${google_service_account.crypto-data-scraper-invoker.email}"
  ]
}

resource "google_project_iam_binding" "cloud-run-invoker-iam" {
  project = "attila-szombati-sandbox"
  role    = "roles/run.invoker"

  members = [
    "serviceAccount:${google_service_account.cloudrun-invoker.email}",
  ]
}

resource "google_project_iam_binding" "secret-manager-iam" {
  project = "attila-szombati-sandbox"
  role    = "roles/secretmanager.secretAccessor"

  members = [
    "serviceAccount:${google_service_account.crypto-data-scraper-invoker.email}",
  ]
}

resource "google_service_account" "storage-admin" {
  account_id   = "cloud-storage-admin"
  display_name = "SA for storage management"
}

resource "google_project_iam_binding" "storage-admin-iam" {
  project = "attila-szombati-sandbox"
  role    = "roles/storage.admin"

  members = [
    "serviceAccount:${google_service_account.storage-admin.email}",
  ]
}
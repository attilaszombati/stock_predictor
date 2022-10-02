resource "google_service_account" "cloudrun-invoker" {
  account_id   = "cloudrun-invoker"
  display_name = "SA for invoke cloud run services"
}

resource "google_project_iam_binding" "cloud-run-invoker-iam" {
  project = "attila-szombati-sandbox"
  role    = "roles/run.invoker"

  members = [
    "serviceAccount:${google_service_account.cloudrun-invoker.email}"
  ]
}

resource "google_service_account" "cloud-run-service-account" {
  account_id   = "cloud-run-service-account"
  display_name = "Cloud run related service account"
}

resource "google_project_iam_binding" "storage-admin-iam" {
  project = "attila-szombati-sandbox"
  role    = "roles/storage.admin"

  members = [
    "serviceAccount:${google_service_account.cloud-run-service-account.email}",
  ]
}

resource "google_project_iam_binding" "secret-manager-reader" {
  project = "attila-szombati-sandbox"
  role    = "roles/secretmanager.admin"

  members = [
    "serviceAccount:${google_service_account.cloud-run-service-account.email}",
  ]
}

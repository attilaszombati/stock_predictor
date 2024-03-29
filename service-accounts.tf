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

resource "google_project_iam_member" "cloud-run-roles" {
  project = "attila-szombati-sandbox"
  for_each = toset([
    "roles/secretmanager.admin",
    "roles/storage.admin",
    "roles/bigquery.admin"
  ])
  role   = each.key
  member = "serviceAccount:${google_service_account.cloud-run-service-account.email}"
}
import os

from google.cloud import storage


class CloudStorageUtils:

    def __init__(self):
        self.storage_client = storage.Client(project=os.getenv('GOOGLE_PROJECT_ID', 'attila-szombati-sandbox'))

    def save_data_to_cloud_storage(self, bucket_name: str, file_name: str, file: str):
        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_filename(file)

    def set_fingerprint_for_user(self, bucket_name: str, file_name: str, fingerprint: str):
        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_string(data=fingerprint)

    def get_fingerprint_for_user(self, bucket_name: str, file_name: str) -> str:
        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(file_name)
        return blob.download_as_text()

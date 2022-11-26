from google.cloud import secretmanager


class SecretManger:
    def __init__(
        self,
    ):
        self.client = secretmanager.SecretManagerServiceClient()

    def get_secret(self, secret_name):
        response = self.client.access_secret_version(request={"name": secret_name})
        payload = response.payload.data.decode("UTF-8")
        return payload

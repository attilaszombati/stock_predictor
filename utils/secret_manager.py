from google.cloud import secretmanager


class SecretManger:

    def __init__(self, ):
        self.client = secretmanager.SecretManagerServiceClient()

    def get_secret(self):
        name = "projects/559224811466/secrets/DB_PASSWORD/versions/2"
        # name = secret_name + '/versions/' + secret_version
        response = self.client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        return payload

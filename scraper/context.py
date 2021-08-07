# pylint:disable=no-name-in-module
# pylint:disable=import-error
from google.cloud import secretmanager
from peewee import MySQLDatabase


def get_secrets():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/crawling-315317/secrets/DB_PASSWORD/versions/1"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
    return payload


def get_mysql_db(password):
    mysql_db = MySQLDatabase(
        user='root',
        password=password,
        unix_socket="/cloudsql/crawling-315317:europe-west1:mysql-03",
        database='twitter',
    )
    return mysql_db

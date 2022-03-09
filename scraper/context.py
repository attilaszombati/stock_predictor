# pylint:disable=missing-module-docstring, no-name-in-module, import-error, missing-function-docstring
from google.cloud import secretmanager
from peewee import MySQLDatabase
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from orm.models import TwitterBaseModel


def get_secrets():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/crawling-315317/secrets/DB_PASSWORD/versions/1"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
    return payload


def get_mysql_db(password: str, database: str = 'twitter'):
    mysql_db = MySQLDatabase(
        user='root',
        password=password,
        unix_socket="/cloudsql/crawling-315317:europe-west1:mysql-03",
        database=database,
    )
    return mysql_db


def init_database(
        user: str = 'postgres',
        password: str = 'postgres',
        container_name: str = 'localhost',
        database: str = 'twitter'
):
    engine = create_engine(
        f'postgresql+psycopg2://{user}:{password}@{container_name}:5432/{database}', echo=True
    )
    if not database_exists(engine.url):
        create_database(engine.url)
    TwitterBaseModel.metadata.create_all(engine)

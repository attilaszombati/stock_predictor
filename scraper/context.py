# pylint:disable=no-name-in-module
from configparser import ConfigParser

import psycopg2
import pymysql
from google.cloud import secretmanager
from peewee import PostgresqlDatabase
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_secrets():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/crawling-315317/secrets/DB_PASSWORD/versions/1"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
    return payload


def get_mysql_db(password: str, database: str = 'twitter'):
    mysql_db = PostgresqlDatabase(
        user='root',
        password=password,
        unix_socket="/cloudsql/crawling-315317:europe-west1:mysql-03",
        database=database,
    )
    return mysql_db


def get_mysql_db_local(password='postgres', database: str = 'twitter'):
    mysql_db = PostgresqlDatabase(
        host='localhost',
        user='postgres',
        database=database,
        password=password,
        port=5432
    )
    return mysql_db


def init_database(password: str = 'postgres', database: str = 'twitter'):
    # TODO switch to postgres

    conn = pymysql.connect(
        unix_socket="/cloudsql/crawling-315317:europe-west1:mysql-03",
        user='root',
        password=password,
    )

    sql = f'CREATE DATABASE IF NOT EXISTS {database}'
    conn.cursor().execute(sql)
    conn.close()


def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db_config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db_config[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')

    return db_config


def init_database_local(database: str = 'twitter'):
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {database}")

    except psycopg2.DatabaseError as error:
        print(error)

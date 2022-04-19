# pylint:disable=no-name-in-module
import os
from configparser import ConfigParser

import psycopg2
import pymysql
from peewee import PostgresqlDatabase
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database


def get_postgres_db():
    db_config = config()
    postgres_db = PostgresqlDatabase(**db_config)
    return postgres_db


def config(filename='../config/database.ini', section='local'):
    if os.getenv("RUNTIME") == "cloud":
        parser = ConfigParser()
        parser.read(filename)

        db_config = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db_config[param[0]] = param[1]
        else:
            raise Exception(f'Section {section} not found in the {filename} file')
    else:
        db_config = {
            # "host": os.getenv("DB_HOST", "35.189.236.175"),
            "host": "/cloudsql/crawling-315317:europe-west1:postgres",
            "user": os.getenv("DB_USER", "root"),
            "database": os.getenv("DB_NAME", "twitter"),
            "password": os.getenv("DB_PASSWORD", "postgrestwitter"),
            "port": os.getenv("DB_PORT", "5432")
        }

    return db_config


def get_mysql_db(password: str, database: str = 'twitter'):
    mysql_db = PostgresqlDatabase(
        user='root',
        password=password,
        unix_socket="/cloudsql/crawling-315317:europe-west1:postgres",
        database=database,
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


def connect_database(database: str = 'twitter'):
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {database}")

    except psycopg2.DatabaseError as error:
        print(error)


def connect_database_sqlalchemy(
        user: str = 'postgres',
        password: str = 'postgres',
        container_name: str = 'localhost',
        database: str = 'twitter'
):
    engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{container_name}:5432/{database}')
    if not database_exists(engine.url):
        create_database(engine.url)

    return engine

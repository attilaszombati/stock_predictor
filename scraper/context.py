# pylint:disable=no-name-in-module
import os
from configparser import ConfigParser

import sqlalchemy
from peewee import PostgresqlDatabase
from sqlalchemy_utils import database_exists, create_database


def get_postgres_db():
    db_config = config()
    postgres_db = PostgresqlDatabase(**db_config)
    return postgres_db


def config(filename='../config/database.ini', section='local'):
    if os.getenv("RUNTIME") != "cloud":
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


def connect_database_sqlalchemy(
        user: str = 'postgres',
        password: str = 'postgres',
        container_name: str = 'localhost',
        database: str = 'twitter'
):
    if os.getenv("RUNTIME") != "cloud":
        engine = sqlalchemy.create_engine(f'postgresql+pg8000://{user}:{password}@{container_name}:5432/{database}')
    else:
        engine = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL.create(
                drivername="postgresql+pg8000",
                username=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME'),
                query={
                    "unix_sock": f"/cloudsql/{str(os.getenv('GOOGLE_PROJECT_ID', 'crawling-315317'))}"
                                 f":europe-west1:postgres2/.s.PGSQL.5432"
                }
            ),
        )
    if not database_exists(engine.url):
        create_database(engine.url)

    return engine

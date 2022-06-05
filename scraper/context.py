# pylint:disable=no-name-in-module
import os

import sqlalchemy
from sqlalchemy_utils import database_exists, create_database


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
                                 f":us-central1:postgres3/.s.PGSQL.5432"
                }
            ),
        )
    if not database_exists(engine.url):
        create_database(engine.url)

    return engine

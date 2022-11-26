# pylint:disable=no-name-in-module

import sqlalchemy
from sqlalchemy_utils import database_exists, create_database


def connect_database_sqlalchemy():
    engine = sqlalchemy.create_engine("sqlite:///:memory:")
    if not database_exists(engine.url):
        create_database(engine.url)

    return engine

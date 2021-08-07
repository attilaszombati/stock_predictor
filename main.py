# pylint:disable=missing-function-docstring, missing-module-docstring
import json

from orm.models import TwitterDataModel
from scraper.context import get_mysql_db, get_secrets, init_database
from scraper.twitter import apply_all_fixture


def handler(request):
    request = json.loads(request)
    user = request.get('USER', '')
    database = request.get('DATABASE', 'twitter')
    print('X' * 50)
    print(f'The user is : {user}, the database is : {database}')
    print('X' * 50)
    payload = get_secrets()

    init_database(database=database,password=payload)

    mysql_db = get_mysql_db(password=payload, database=database)

    mysql_db.create_tables([TwitterDataModel])
    apply_all_fixture(user)
    return {'done': 1}

# pylint:disable=missing-function-docstring, missing-module-docstring
from orm.models import TwitterDataModel
from scraper.context import get_mysql_db, get_secrets, init_database
from scraper.twitter import apply_all_fixture


def handler(request):
    print(request)
    payload = get_secrets()

    init_database(password=payload)

    mysql_db = get_mysql_db(password=payload)

    mysql_db.create_tables([TwitterDataModel])
    apply_all_fixture()
    return {'done': 1}

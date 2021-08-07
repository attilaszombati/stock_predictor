# pylint:disable=missing-function-docstring, missing-module-docstring
import json

from orm.models import TwitterDataModel
from scraper.context import get_mysql_db, get_secrets, init_database
from scraper.twitter import apply_all_fixture

tables = {
    'elonmusk': 'elon_musk',
    'JeffBezos': 'jeff_besos'
}

def handler(request):
    request = request.get_data()
    try:
        request_json = json.loads(request.decode())
    except ValueError as json_error:
        print(f"Error decoding JSON: {json_error}")
        return "JSON Error", 400
    user = request_json.get('USER', '')
    database = request_json.get('DATABASE', 'twitter')
    payload = get_secrets()
    init_database(database=database, password=payload)
    mysql_db = get_mysql_db(password=payload, database=database)
    TwitterDataModel.Meta.table_name = tables.get(user)
    mysql_db.create_tables([TwitterDataModel])
    apply_all_fixture(user)
    return {'done': 1}

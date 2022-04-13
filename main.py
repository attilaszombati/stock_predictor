# pylint:disable=missing-function-docstring, missing-module-docstring
import json

from utils.secret_manager import SecretManger
from scraper.context import get_mysql_db, init_database
from scraper.twitter import apply_all_fixture, user_models


def handler(request):
    request = request.get_data()
    try:
        request_json = json.loads(request.decode())
    except ValueError as json_error:
        print(f"Error decoding JSON: {json_error}")
        return "JSON Error", 400
    users = request_json.get('USERS', '')
    database = request_json.get('DATABASE', 'twitter')
    scraping_type = request_json.get('SCRAPING_TYPE', 'since')
    payload = SecretManger().get_secret(secret_name='', secret_version='')
    init_database(database=database, password=payload)
    mysql_db = get_mysql_db(password=payload, database=database)
    for user in users:
        table = user_models.get(user)
        mysql_db.create_tables([table])
        apply_all_fixture(scraping_type=scraping_type, twitter_user=user)
    return {'done': 1}

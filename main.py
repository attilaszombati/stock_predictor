# pylint:disable=no-name-in-module, unexpected-keyword-arg

import pandas as pd

from scraper.context import connect_database_sqlalchemy
from scraper.twitter import apply_all_fixture, user_models


def main(user: str = 'elonmusk', scraping_type: str = 'since'):
    postgres_engine = connect_database_sqlalchemy(database='twitter')
    user_models.get(user).metadata.create_all(postgres_engine)
    last_tweeted_at = apply_all_fixture(scraping_type=scraping_type, twitter_user=user, engine=postgres_engine)
    user_df = pd.read_sql(
        """
        select * from elon_musk
        """,
        postgres_engine
    )

    user_df.to_parquet(path=f'{user}_{last_tweeted_at}.pq', compression='snappy')


def handler(request):
    request = request.get_data()
    print(request)
    # try:
    #     request_json = json.loads(request.decode())
    # except ValueError as json_error:
    #     print(f"Error decoding JSON: {json_error}")
    #     return "JSON Error", 400
    # users = request_json.get('USERS', '')
    # scraping_type = request_json.get('SCRAPING_TYPE', 'since')
    # payload = SecretManger().get_secret()
    main(user='elonmusk', scraping_type='since')
    return {'done': 1}

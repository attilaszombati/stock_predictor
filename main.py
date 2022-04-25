# pylint:disable=no-name-in-module, unexpected-keyword-arg
import json

import pandas as pd
from sqlalchemy.orm import Session

from scraper.context import connect_database_sqlalchemy
from scraper.twitter import user_models, TwitterNewsScraper, TwitterHistoryScraper
from utils.cloud_storage import CloudStorageUtils
from utils.postgres_instance import update_postgres_instance_status

user_tables = {
    'elonmusk': "elon_musk",
    'JeffBezos': "jeff_bezos",
    'BarackObama': "barack_obama",
    'JoeBiden': "joe_biden",
    'KamalaHarris': "kamala_harris",
}


def main(user: str = 'elonmusk', scraping_type: str = 'news'):
    postgres_engine = connect_database_sqlalchemy(database='twitter')
    user_models.get(user).metadata.create_all(postgres_engine)
    storage = CloudStorageUtils()
    postgres_table = user_tables.get(user)

    with Session(postgres_engine) as session:
        if scraping_type == 'news':
            fingerprint = storage.get_fingerprint_for_user(
                bucket_name='twitter_scraped_data',
                file_name=f'{postgres_table}/fingerprint.csv'
            )
            scraper = TwitterNewsScraper(user=user, database_session=session, last_scraped_tweet=fingerprint)
            batch = scraper.scraping_data_news()
        else:
            scraper = TwitterHistoryScraper(user=user, database_session=session)
            batch = scraper.set_query_for_history_scraper()

    last_tweeted_at = scraper.load_scraped_data(engine=postgres_engine, scraped_batch=batch)

    user_df = pd.read_sql(
        f"""
        select * from {postgres_table}
        """,
        postgres_engine
    )

    user_df.to_parquet(path=f'/tmp/{postgres_table}_{last_tweeted_at}.pq', compression='snappy')
    storage.save_data_to_cloud_storage(bucket_name='twitter_scraped_data',
                                       file_name=f'{postgres_table}/{last_tweeted_at}.pq',
                                       parquet_file=f'/tmp/{postgres_table}_{last_tweeted_at}.pq')
    storage.set_fingerprint_for_user(bucket_name='twitter_scraped_data',
                                     file_name=f'{postgres_table}/fingerprint.csv',
                                     fingerprint=last_tweeted_at)


def handler(request):
    request = request.get_data()
    try:
        request_json = json.loads(request.decode())
    except ValueError as json_error:
        print(f"Error decoding JSON: {json_error}")
        return "JSON Error", 400
    users = request_json.get('TWITTER_USER', '')
    scraping_type = request_json.get('SCRAPING_TYPE', 'since')
    main(user=users, scraping_type=scraping_type)
    return {'done': 1}


def handler_postgres(request):
    update_postgres_instance_status(request)

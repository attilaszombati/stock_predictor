# pylint:disable=no-name-in-module, unexpected-keyword-arg
import json
import os

import pandas as pd
from google.cloud import storage
from sqlalchemy.orm import Session

from scraper.context import connect_database_sqlalchemy
from scraper.twitter import user_models, TwitterNewsScraper, TwitterHistoryScraper

storage_client = storage.Client(project=os.getenv('GOOGLE_PROJECT_ID', 'crawling-315317'))


def main(user: str = 'elonmusk', scraping_type: str = 'news'):
    postgres_engine = connect_database_sqlalchemy(database='twitter')
    user_models.get(user).metadata.create_all(postgres_engine)
    with Session(postgres_engine) as session:
        if scraping_type == 'news':
            scraper = TwitterNewsScraper(user=user, database_session=session)
            batch = scraper.scraping_data_news()
        else:
            scraper = TwitterHistoryScraper(user=user, database_session=session)
            batch = scraper.set_query_for_history_scraper()

    last_tweeted_at = scraper.load_scraped_data(engine=postgres_engine, scraped_batch=batch)
    user_df = pd.read_sql(
        """
        select * from elon_musk
        """,
        postgres_engine
    )

    user_df.to_parquet(path=f'/tmp/{user}_{last_tweeted_at}.pq', compression='snappy')
    save_data_to_cloud_storage(bucket_name='twitter_scraped_data',
                               file_name=f'{user}_{last_tweeted_at}.pq',
                               parquet_file=f'/tmp/{user}_{last_tweeted_at}.pq')


def save_data_to_cloud_storage(bucket_name: str, file_name: str, parquet_file: str):
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(parquet_file)


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

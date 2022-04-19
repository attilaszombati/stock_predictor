# pylint:disable=no-name-in-module, unexpected-keyword-arg
import json
import os

import pandas as pd
from google.cloud import storage

from scraper.context import connect_database_sqlalchemy
from scraper.twitter import apply_all_fixture, user_models

storage_client = storage.Client(project=os.getenv('GOOGLE_PROJECT_ID', 'crawling-315317'))


def main(user: str = 'elonmusk', scraping_type: str = 'since'):
    postgres_engine = connect_database_sqlalchemy(database='twitter')
    user_models.get(user).metadata.create_all(postgres_engine)
    last_tweeted_at = apply_all_fixture(scraping_type=scraping_type, twitter_user=user, engine=postgres_engine)
    user_df = pd.read_sql(
        f"""
        select * from {user.lower()}
        """,
        postgres_engine
    )

    user_df.to_parquet(path=f'/tmp/{user}_{last_tweeted_at}.pq', compression='snappy')
    save_data_to_cloud_storage(bucket_name=f'twitter_scraped_data/{user}',
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

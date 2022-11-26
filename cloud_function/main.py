# pylint:disable=no-name-in-module, unexpected-keyword-arg
import os

import pandas as pd
from flask import Flask, request
from scraper.context import connect_database_sqlalchemy
from scraper.twitter import user_models, TwitterNewsScraper, TwitterHistoryScraper
from sqlalchemy.orm import Session
from utils.cloud_storage import CloudStorageUtils

user_tables = {
    "elonmusk": "elon_musk",
    "JeffBezos": "jeff_bezos",
    "BarackObama": "barack_obama",
    "JoeBiden": "joe_biden",
    "KamalaHarris": "kamala_harris",
}

app = Flask(__name__)


def main(user: str = "elonmusk", scraping_type: str = "news"):
    postgres_engine = connect_database_sqlalchemy()
    user_models.get(user).metadata.create_all(postgres_engine)
    storage = CloudStorageUtils()
    postgres_table = user_tables.get(user)

    with Session(postgres_engine) as session:
        if scraping_type == "news":
            fingerprint = storage.get_fingerprint_for_user(
                bucket_name="twitter_data_collection",
                file_name=f"{postgres_table}/fingerprint.csv",
            )
            scraper = TwitterNewsScraper(
                user=user, database_session=session, last_scraped_tweet=fingerprint
            )
            batch = scraper.scraping_data_news()
        else:
            scraper = TwitterHistoryScraper(user=user, database_session=session)
            batch = scraper.set_query_for_history_scraper()

        last_tweeted_at = scraper.load_scraped_data(
            engine=postgres_engine, scraped_batch=batch
        )

        user_df = pd.read_sql(
            f"""
            select * from {postgres_table}
            """,
            postgres_engine,
        )

    if last_tweeted_at:
        user_df.to_parquet(
            path=f"/tmp/{postgres_table}_{last_tweeted_at}.pq", compression="snappy"
        )
        storage.save_data_to_cloud_storage(
            bucket_name="twitter_data_collection",
            file_name=f"{postgres_table}/{last_tweeted_at}.pq",
            file=f"/tmp/{postgres_table}_{last_tweeted_at}.pq",
        )
        storage.set_fingerprint_for_user(
            bucket_name="twitter_data_collection",
            file_name=f"{postgres_table}/fingerprint.csv",
            fingerprint=last_tweeted_at,
        )


@app.route("/", methods=["POST"])
def handler():
    data = request.get_json()
    users = data.get("TWITTER_USERS", [])
    if users is None:
        raise ValueError("No users provided")
    scraping_type = data.get("SCRAPING_TYPE", "since")
    if scraping_type not in ["since", "news"]:
        raise ValueError("Scraping type not supported")
    for user in users:
        main(user=user, scraping_type=scraping_type)
    return {"done": 1}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

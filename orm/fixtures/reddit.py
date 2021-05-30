import time
from datetime import datetime
import pymysql
import snscrape.modules.reddit as snreddit

from snscrape.base import ScraperException

from orm.models import mysql_db, RedditDataModel


# Using RedditSubredditScraper to scrape data
def scraping_data(last_saved=None):
    for i, reddit in enumerate(
            snreddit.RedditSubredditScraper(name='wallstreetbets',
                                            comments=False, before='1613751542').get_items()):
        try:
            last_saved = reddit
            yield reddit
        except Exception:
            print(last_saved)
            time.sleep(100)
            scraping_data(last_saved=datetime.fromisoformat(str(last_saved.created)).timestamp())


def create_models_from_scraping():
    yield from (
        RedditDataModel(
            author=data.author,
            created_at=data.created,
            post_id=data.id,
            self_text=data.selftext,
            subreddit=data.subreddit,
            title=data.title,
            url=data.url
        ) for data in scraping_data())

def apply_all_fixture():
    for f in create_models_from_scraping():
        f.insert_if_not_exists()


def init_database():
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='',
    )

    sql = (
        f'CREATE DATABASE IF NOT EXISTS reddit'
    )
    conn.cursor().execute(sql)
    conn.close()


if __name__ == '__main__':
    # init_database()
    # mysql_db# .create_tables([RedditDataModel])
    apply_all_fixture()
    # scraping_data()

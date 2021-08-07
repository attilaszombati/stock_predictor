# pylint:disable=import-error
import pymysql
import snscrape.modules.reddit as snreddit

from orm.models import RedditDataModel


# Using RedditSubredditScraper to scrape data
def scraping_data(last_saved=None):
    for reddit in snreddit.RedditSubredditScraper(
        name='wallstreetbets', comments=False, before='1613751542'
    ).get_items():
        yield reddit


def create_models_from_scraping():
    yield from (
        RedditDataModel(
            author=data.author,
            created_at=data.created,
            post_id=data.id,
            self_text=data.selftext,
            subreddit=data.subreddit,
            title=data.title,
            url=data.url,
        )
        for data in scraping_data()
    )


def apply_all_fixture():
    for f in create_models_from_scraping():
        f.insert_if_not_exists()


def init_database(password):
    conn = pymysql.connect(
        unix_socket="/cloudsql/crawling-315317:europe-west1:mysql-03",
        user='root',
        password=password,
    )

    sql = 'CREATE DATABASE IF NOT EXISTS reddit'
    conn.cursor().execute(sql)
    conn.close()


if __name__ == '__main__':
    # init_database()
    # mysql_db# .create_tables([RedditDataModel])
    apply_all_fixture()
    # scraping_data()

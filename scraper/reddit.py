# pylint:disable=import-error
import snscrape.modules.reddit as snreddit

from orm.models import RedditDataModel
# Using RedditSubredditScraper to scrape data
from scraper.context import init_database


def scraping_data(last_saved=None):
    # pylint:disable=no-member
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


if __name__ == '__main__':
    init_database(password='', database='reddit')
    # mysql_db# .create_tables([RedditDataModel])
    apply_all_fixture()
    # scraping_data()

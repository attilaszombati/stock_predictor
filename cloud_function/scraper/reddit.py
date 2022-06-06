# pylint:disable=import-error, missing-function-docstring, missing-module-docstring
import snscrape.modules.reddit as snreddit

from orm.models import RedditDataModel


def scraping_data():
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


def apply_all_fixture_from_reddit():
    for fixture in create_models_from_scraping():
        fixture.insert_if_not_exists()


if __name__ == '__main__':
    apply_all_fixture_from_reddit()

# pylint:disable=no-name-in-module
import os
import time
from datetime import datetime

from praw import Reddit

from orm.models import RedditOfficialApiModel, postgres_db

reddit = Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID", ""),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
    user_agent=os.getenv("REDDIT_USER_AGENT", "")
)


def get_last_record_timestamp():
    hole = datetime.fromisoformat(str(RedditOfficialApiModel.get())).timestamp()
    print(hole)
    return str(hole)


def get_official_reddit_data():
    max_post = reddit.subreddit("wallstreetbets").new(limit=None)
    batch = []
    for i, post in enumerate(max_post):
        batch.append(post)
        if i % 100 == 0:
            yield from batch
            print('We will wait..')
            time.sleep(100)
            batch = []
        else:
            continue


def official_reddit_api():
    yield from (
        RedditOfficialApiModel(
            author=data.author,
            title=data.title,
            score=data.score,
            num_comments=data.num_comments,
            self_text=data.selftext,
            created_at=datetime.fromtimestamp(data.created).strftime('%Y-%m-%d %H:%M:%S.%f'),
            total_awards_received=data.total_awards_received,
            post_id=data.id,
            subreddit=data.subreddit,
            subreddit_id=data.subreddit_id,
            url=data.url,
            view_count=data.view_count,
            # upvote=data.upvote,
            # upvote_ratio=data.upvote_ratio,
        )
        for data in get_official_reddit_data()
    )


def apply_all_fixture():
    for fixture in official_reddit_api():
        fixture.insert_if_not_exists()


if __name__ == '__main__':
    postgres_db.create_tables([RedditOfficialApiModel])
    apply_all_fixture()

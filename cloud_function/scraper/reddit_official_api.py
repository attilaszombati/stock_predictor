# pylint:disable=no-name-in-module, no-member
import os
import time
from datetime import datetime

import pandas as pd
from praw import Reddit
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from cloud_function.orm.models import RedditOfficialApiModel
from cloud_function.scraper.context import connect_database_sqlalchemy

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


def load_scraped_data(engine: Engine):
    with Session(engine) as sess:
        for fixture in official_reddit_api():
            sess.add(fixture)
            sess.commit()

        return str(RedditOfficialApiModel.get_newest_reddit_elem(sess).posted_at).replace(" ", "-")


if __name__ == '__main__':
    postgres_engine: Engine = connect_database_sqlalchemy()
    load_scraped_data(engine=postgres_engine)

    last_tweeted_at = load_scraped_data(engine=postgres_engine)
    df = pd.read_sql(
        """
        select * from wallstreetbets_official_api
        """,
        postgres_engine
    )

    df.to_parquet(path=f'wallstreetbets_official_api_{last_tweeted_at}.pq', compression='snappy')

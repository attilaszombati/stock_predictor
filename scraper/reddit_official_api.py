# pylint:disable=import-error
import time
from datetime import datetime

from praw import Reddit

from orm.models import RedditOfficialApiModel, mysql_db

reddit = Reddit(
    client_id='YgNm5NHkXxrMwA',
    client_secret='_OA_8yPNDDGufG9VSSxLx2mvPsPQFw',
    user_agent='szates_96',
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
    for f in official_reddit_api():
        f.insert_if_not_exists()


if __name__ == '__main__':
    # for i, post in enumerate(reddit.subreddit("wallstreetbets").new(limit=1)):
    #     if i < 2:
    #         print(dir(post))
    #         print(post.created)
    mysql_db.create_tables([RedditOfficialApiModel])
    apply_all_fixture()
    # print([datetime.fromtimestamp(i.created).strftime('%Y-%m-%d %H:%M:%S.%f')
    #       for i in reddit.subreddit("wallstreetbets").new(limit=600, params={'before': 1618513660})])

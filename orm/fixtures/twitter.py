import pymysql
import snscrape.modules.twitter as sntwitter
import snscrape.modules.reddit as snreddit
# Creating list to append tweet data to
from playhouse.shortcuts import model_to_dict

from orm.models import TwitterDataModel, mysql_db


# tweets_list1 = []

# Using TwitterSearchScraper to scrape data and append tweets to list
def scraping_data():
    max_item = sntwitter.TwitterSearchScraper('from:JeffBezos').get_items()
    for i, tweet in enumerate(max_item):
        try:
            yield tweet
        except StopIteration:
            raise StopIteration('End of scraping')
        else:
            continue


def scraping_data_from_hashtag():
    max_item = sntwitter.TwitterHashtagScraper('bitcoin').get_items()
    preprocess = sorted(max_item, key=lambda x: x.replyCount > 10 and x.retweetCount > 10 and x.likeCount > 10)
    for i, tweet in enumerate(preprocess):
        try:
            yield tweet
        except StopIteration:
            raise StopIteration('End of scraping')
        else:
            continue


def create_models_from_scraping():
    yield from (
        TwitterDataModel(
            user_name=data.user.username,
            created_at=data.date,
            reply_count=data.replyCount,
            retweet_count=data.retweetCount,
            like_count=data.likeCount,
            url=data.url
        ) for data in scraping_data_from_hashtag())


# Creating a dataframe from the tweets list above
# tweets_df1 = pd.DataFrame(tweets_list1, columns=['Datetime', 'Tweet Id', 'Text', 'Username'])
# print(tweets_df1)

def apply_all_fixture():

    for f in create_models_from_scraping():
        data = model_to_dict(f, recurse=False)
        f.insert(data).on_conflict(update=data).execute()


def init_database():
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='',
    )

    sql = (
        f'CREATE DATABASE IF NOT EXISTS twitter'
    )
    conn.cursor().execute(sql)
    conn.close()


if __name__ == '__main__':
    # init_database()
    mysql_db.create_tables([TwitterDataModel])
    apply_all_fixture()

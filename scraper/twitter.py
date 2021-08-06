from datetime import datetime

import pymysql
import snscrape.modules.twitter as sntwitter
from playhouse.shortcuts import model_to_dict

# Using TwitterSearchScraper to scrape data and append tweets to list
from orm.models import TwitterDataModel
from scraper.context import mysql_db


def scraping_data():
    last_scraped = TwitterDataModel.get_latest_elem_from_table()
    if last_scraped:
        last_record_time = datetime.strptime(str(last_scraped.created_at), "%Y-%m-%d %H:%M:%S")
        since_time = f'since_time:{last_record_time.timestamp()}'
        print(f'The since_time variable is : {since_time}')
    else:
        since_time = 'since_time:964381815'
    query = f'from:elonmusk {since_time[:-2]}'
    print(f'The search query is : {query}')
    max_item = sntwitter.TwitterSearchScraper(query).get_items()
    for i, tweet in enumerate(max_item):
        yield tweet
    print('X' * 50)
    print('End of scraping')
    print('X' * 50)


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
            cashtags=data.cashtags,
            content=data.content,
            conversation_id=data.conversationId,
            coordinates=data.coordinates,
            created_at=data.date,
            hastags=data.hashtags,
            in_reply_to_tweet_id=data.inReplyToTweetId,
            in_reply_to_user=data.inReplyToUser,
            language=data.lang,
            like_count=data.likeCount,
            mentioned_users=data.mentionedUsers,
            outlinks=data.outlinks,
            place=data.place,
            quote_count=data.quoteCount,
            quoted_tweet=data.quotedTweet,
            reply_count=data.replyCount,
            retweet_count=data.retweetCount,
            retweeted_tweet=data.retweetedTweet,
            source=data.source,
            source_url=data.sourceUrl,
            url=data.url,
            # scraped_at=data.scraped_at,
            user_name=data.user.username,
        ) for data in scraping_data())


def apply_all_fixture():
    for f in create_models_from_scraping():
        data = model_to_dict(f, recurse=False)
        f.insert(data).on_conflict(update=data).execute()


def init_database():
    conn = pymysql.connect(
        unix_socket="/cloudsql/crawling-315317:europe-west1:mysql-03",
        user='root',
        password='attilaattila123',
    )

    sql = (
        f'CREATE DATABASE IF NOT EXISTS twitter'
    )
    conn.cursor().execute(sql)
    conn.close()


def handler():
    init_database()
    mysql_db.create_tables([TwitterDataModel])
    apply_all_fixture()


if __name__ == '__main__':
    handler()

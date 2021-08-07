# pylint:disable=missing-function-docstring, missing-module-docstring
# pylint:disable=import-error
from datetime import datetime

import snscrape.modules.twitter as sntwitter
from playhouse.shortcuts import model_to_dict

# Using TwitterSearchScraper to scrape data and append tweets to list
from orm.models import TwitterDataModel

tables = {
    'elonmusk': 'elon_musk',
    'JeffBezos': 'jeff_besos'
}

def scraping_data(user: str = 'elonmusk'):
    TwitterDataModel.set_table_name(tables.get(user))
    last_scraped = TwitterDataModel.get_latest_elem_from_table()
    if last_scraped:
        last_record_time = datetime.strptime(str(last_scraped.created_at), "%Y-%m-%d %H:%M:%S")
        since_time = f'since_time:{last_record_time.timestamp()}'
        print(f'The since_time variable is : {since_time}')
    else:
        since_time = 'since_time:964381815'
    query = f'from:{user} {since_time[:-2]}'
    print(f'The search query is : {query}')
    max_item = sntwitter.TwitterSearchScraper(query).get_items()
    for tweet in max_item:
        yield tweet
    print('X' * 50)
    print('End of scraping')
    print('X' * 50)


def scraping_data_from_hashtag():
    max_item = sntwitter.TwitterHashtagScraper('bitcoin').get_items()
    preprocess = sorted(
        max_item, key=lambda x: x.replyCount > 10 and x.retweetCount > 10 and x.likeCount > 10
    )
    for tweet in preprocess:
        yield tweet


def create_models_from_scraping(user):
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
        )
        for data in scraping_data(user=user)
    )


def apply_all_fixture(user):
    for fixture in create_models_from_scraping(user=user):
        data = model_to_dict(fixture, recurse=False)
        fixture.insert(data).on_conflict(update=data).execute()

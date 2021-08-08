# pylint:disable=missing-function-docstring, missing-module-docstring
# pylint:disable=import-error
import logging
import time
from datetime import datetime

import snscrape.modules.twitter as sntwitter
from playhouse.shortcuts import model_to_dict

# Using TwitterSearchScraper to scrape data and append tweets to list
from orm.models import (
    TwitterDataModelElonMusk,
    TwitterDataModelJeffBezos,
    TwitterDataModelBarackObama,
    TwitterDataModelJoeBiden,
    TwitterDataModelKamalaHarris
)

tables = {
    'elonmusk': TwitterDataModelElonMusk,
    'JeffBezos': TwitterDataModelJeffBezos,
    'BarackObama': TwitterDataModelBarackObama,
    'JoeBiden': TwitterDataModelJoeBiden,
    'KamalaHarris': TwitterDataModelKamalaHarris,
}

logger = logging.getLogger(__name__)

def scraping_data(scraping_type: str = 'since', user: str = 'elonmusk'):
    if scraping_type == 'since':
        last_scraped = tables.get(user).get_latest_elem_from_table()
    else:
        last_scraped = tables.get(user).get_oldest_elem_from_table()

    if last_scraped:
        last_record_time = datetime.strptime(str(last_scraped.created_at), "%Y-%m-%d %H:%M:%S")
        since_time = f'{scraping_type}_time:{last_record_time.timestamp()}'
        print(f'The {scraping_type}_time variable is : {since_time}')
    else:
        since_time = 'since_time:964381815'

    if scraping_type == 'since' and int(time.time()) - 86400 > int(last_record_time.timestamp()):
        query = f'from:{user} {since_time[:-2]} until_time:{int(time.time()) - 86400}'
        print(f'The search query is : {query}')
        max_item = sntwitter.TwitterSearchScraper(query).get_items()
        for tweet in max_item:
            yield tweet
    else:
        logger.warning('Need to wait more time! At least 1 day after the last tweet')
        print('Need to wait more time!')
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


def create_models_from_scraping(scraping_type, user):
    yield from (
        tables.get(user)(
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
        for data in scraping_data(scraping_type=scraping_type, user=user)
    )


def apply_all_fixture(scraping_type, user):
    for fixture in create_models_from_scraping(scraping_type=scraping_type, user=user):
        data = model_to_dict(fixture, recurse=False)
        fixture.insert(data).on_conflict(update=data).execute()

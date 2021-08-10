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

def scraping_data_history(user: str = 'elonmusk'):
    last_scraped = tables.get(user).get_oldest_elem_from_table()

    if last_scraped:
        last_record_time = datetime.strptime(str(last_scraped.created_at), "%Y-%m-%d %H:%M:%S")
        scraper_time = f'until_time:{last_record_time.timestamp()}'
        print(f'The until_time variable is : {scraper_time}')
    else:
        scraper_time = 'since_time:964381815'

    query = f'from:{user} {scraper_time[:-2]}'
    print(f'The search query is : {query}')
    max_item = sntwitter.TwitterSearchScraper(query).get_items()
    for tweet in max_item:
        yield tweet
    print('X' * 50)
    print('End of history scraping')
    print('X' * 50)


def scraping_data_news(user: str = 'elonmusk'):
    last_scraped = tables.get(user).get_latest_elem_from_table()
    if last_scraped:
        last_record_time = datetime.strptime(str(last_scraped.created_at), "%Y-%m-%d %H:%M:%S")
        scraper_time = f'since_time:{last_record_time.timestamp()}'
        print(f'The since_time variable is : {scraper_time}')
    else:
        scraper_time = 'since_time:964381815'

    query = f'from:{user} {int(scraper_time[:-2]) + 1} until_time:{int(time.time() - (86400 * 3))}'
    print(f'The search query is : {query}')
    max_item = sntwitter.TwitterSearchScraper(query).get_items()
    for tweet in max_item:
        if tweet:
            yield tweet
        else:
            logger.warning('Need to wait more time! At least 3 day after the last tweet')
    print('X' * 50)
    print('End of new feeds scraping')
    print('X' * 50)


def scraping_data_from_hashtag():
    max_item = sntwitter.TwitterHashtagScraper('bitcoin').get_items()
    preprocess = sorted(
        max_item, key=lambda x: x.replyCount > 10 and x.retweetCount > 10 and x.likeCount > 10
    )
    for tweet in preprocess:
        yield tweet


def create_models_from_scraping(scraping_type, user):
    if scraping_type == 'since':
        scraping_batch = scraping_data_news(user=user)
    else:
        scraping_batch = scraping_data_history(user=user)

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
        for data in scraping_batch
    )


def apply_all_fixture(scraping_type, user):
    for fixture in create_models_from_scraping(scraping_type=scraping_type, user=user):
        data = model_to_dict(fixture, recurse=False)
        fixture.insert(data).on_conflict(update=data).execute()

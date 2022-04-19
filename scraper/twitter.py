# pylint:disable=no-name-in-module
import logging
import time
from datetime import datetime

import pandas as pd
import snscrape.modules.twitter as sntwitter
from sqlalchemy.orm import Session

from orm.models import (
    TwitterDataModelElonMusk,
    TwitterDataModelJeffBezos,
    TwitterDataModelBarackObama,
    TwitterDataModelJoeBiden,
    TwitterDataModelKamalaHarris,
)
from scraper.context import connect_database_sqlalchemy
from scraper.custom_exceptions import UserModelNotFound

user_models = {
    'elonmusk': TwitterDataModelElonMusk,
    'JeffBezos': TwitterDataModelJeffBezos,
    'BarackObama': TwitterDataModelBarackObama,
    'JoeBiden': TwitterDataModelJoeBiden,
    'KamalaHarris': TwitterDataModelKamalaHarris,
}

logger = logging.getLogger('twitter-scraper')


class TwitterScraperConfig:

    def __init__(self, user: str):
        self.user = user
        self.query_time = None
        self.since_time_str = 'since_time:964381815'
        self.since_time_int = 964381815
        self.time_delta = 3


class TwitterScraper(TwitterScraperConfig):

    def __init__(self, user: str, scraping_type: str, session):
        super().__init__(user)
        self.user = user
        self.query_time = None
        self.scraping_type = scraping_type
        self.session: Session = session

    def validate_user_model(self):
        if self.user not in user_models:
            raise UserModelNotFound(self.user)

    @property
    def get_last_scraped_tweet(self):
        return user_models.get(self.user).get_oldest_elem_from_table(session=self.session)

    def set_query_time_until_last_scraped(self):
        last_record_time = datetime.strptime(str(self.get_last_scraped_tweet.tweeted_at), "%Y-%m-%d %H:%M:%S")
        logger.warning(f'Old tweets for the user : {self.user} '
                       f'will be scraped from : {last_record_time}')
        logger.info(f'The until_time variable is : {self.query_time}')
        self.query_time = f'until_time:{last_record_time.timestamp()}'
        return self.query_time

    def set_query_time_from_last_scraped(self):
        last_record_time = datetime.strptime(str(self.get_last_scraped_tweet.tweeted_at), "%Y-%m-%d %H:%M:%S")
        scraper_time = int(last_record_time.timestamp()) + 1
        self.query_time = f'since_time:{scraper_time}'
        logger.info(f'New tweets for the user : {self.user} will be scraped from: {self.query_time}')
        logger.info(f'The until_time variable is : {self.query_time}')
        return self.query_time

    def scraping_data_history(self):
        if self.get_last_scraped_tweet:
            scraper_time = self.set_query_time_until_last_scraped()
        else:
            scraper_time = self.since_time_str

        query = f'from:{self.user} {scraper_time[:-2]}'
        logger.info(f'The search query is : {query}')
        tweets = sntwitter.TwitterSearchScraper(query).get_items()
        for tweet in tweets:
            yield tweet

    def scraping_data_news(self):
        if self.get_last_scraped_tweet:
            since_time = self.set_query_time_from_last_scraped()
        else:
            scraper_time = self.since_time_int
            since_time = f'since_time:{scraper_time}'

        until_time = int(time.time() - (86400 * 3))
        query = f'from:{self.user} {since_time} until_time:{until_time}'
        logger.info(f'The search query is : {query}')
        tweets = sntwitter.TwitterSearchScraper(query).get_items()
        for tweet in tweets:
            if tweet:
                yield tweet
            else:
                logger.warning('Need to wait more time! At least 3 day after the last tweet')

    def create_models_from_scraping(self, scraping_type, twitter_user):
        if scraping_type == 'since':
            scraping_batch = self.scraping_data_news()
        else:
            scraping_batch = self.scraping_data_history()

        yield from (
            user_models.get(twitter_user)(
                id=data.id,
                cashtags=data.cashtags,
                content=data.content,
                conversation_id=data.conversationId,
                coordinates=data.coordinates,
                tweeted_at=data.date,
                hashtags=data.hashtags,
                in_reply_to_tweet_id=data.inReplyToTweetId,
                in_reply_to_user=check_reply(data.inReplyToUser),
                language=data.lang,
                like_count=data.likeCount,
                mentioned_users=check_mentioned(data.mentionedUsers),
                outlinks=data.outlinks,
                place=data.place,
                quote_count=data.quoteCount,
                quoted_tweet=check_quoted_tweet(data.quotedTweet),
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


def check_mentioned(data):
    if data is not None:
        return ''.join([mentioned.username for mentioned in data])
    return data


def check_quoted_tweet(data):
    if data is not None:
        return str(data.url)
    return data


def check_reply(data):
    if data is not None:
        return str(data.username)
    return data


def scraping_data_from_hashtag():
    max_item = sntwitter.TwitterHashtagScraper('bitcoin').get_items()
    preprocess = sorted(
        max_item, key=lambda x: x.replyCount > 10 and x.retweetCount > 10 and x.likeCount > 10
    )
    for tweet in preprocess:
        yield tweet


def apply_all_fixture(scraping_type, twitter_user, engine):
    with Session(engine) as session:
        scraper = TwitterScraper(user=twitter_user, scraping_type=scraping_type, session=session)
        for fixture in scraper.create_models_from_scraping(scraping_type=scraping_type, twitter_user=twitter_user):
            session.add(fixture)
            session.commit()

    return str(scraper.get_last_scraped_tweet.tweeted_at).replace(" ", "-")


if __name__ == '__main__':
    postgres_engine = connect_database_sqlalchemy(database='twitter')
    TwitterDataModelJoeBiden.metadata.create_all(postgres_engine)
    last_tweeted_at = apply_all_fixture(scraping_type='old', twitter_user='JoeBiden', engine=postgres_engine)
    df = pd.read_sql(
        """
        select * from elon_musk
        """,
        postgres_engine
    )

    df.to_parquet(path=f'joe_biden_{last_tweeted_at}.pq', compression='snappy')

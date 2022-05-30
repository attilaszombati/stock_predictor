# pylint:disable=no-name-in-module
import logging
import time
from datetime import datetime

import pandas as pd
import snscrape.modules.twitter as sntwitter
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from orm.models import (
    TwitterDataModelElonMusk,
    TwitterDataModelJeffBezos,
    TwitterDataModelBarackObama,
    TwitterDataModelJoeBiden,
    TwitterDataModelKamalaHarris,
)
from scraper.context import connect_database_sqlalchemy
from scraper.custom_exceptions import UserModelNotFound, NewsScraperMissConfigured

user_models = {
    'elonmusk': TwitterDataModelElonMusk,
    'JeffBezos': TwitterDataModelJeffBezos,
    'BarackObama': TwitterDataModelBarackObama,
    'JoeBiden': TwitterDataModelJoeBiden,
    'KamalaHarris': TwitterDataModelKamalaHarris,
}

logger = logging.getLogger('twitter-scraper')


class TwitterScraperBase:

    def __init__(self, user: str, database_session):
        self.user = user
        self.query_time = None
        self.since_time_str = 'since_time:964381815'
        self.since_time_int = 964381815
        self.time_delta = 3
        self.session: Session = database_session

    def validate_user_model(self):
        if self.user not in user_models:
            raise UserModelNotFound(self.user)

    def get_last_scraped_tweet(self):
        return user_models.get(self.user).get_oldest_tweeted_at_elem(session=self.session)

    def get_newest_scraped_tweet(self):
        return user_models.get(self.user).get_newest_tweeted_at_elem(session=self.session)

    @staticmethod
    def start_scraping(query):
        tweets = sntwitter.TwitterSearchScraper(query).get_items()
        for tweet in tweets:
            print(tweet.__dict__)
            yield tweet

    @staticmethod
    def check_mentioned(data):
        if data is not None:
            return ''.join([mentioned.username for mentioned in data])
        return data

    @staticmethod
    def check_quoted_tweet(data):
        if data is not None:
            return str(data.url)
        return data

    @staticmethod
    def check_reply(data):
        if data is not None:
            return str(data.username)
        return data

    @staticmethod
    def check_outlinks(data):
        if data is not None:
            return ','.join(link for link in data)
        return data

    def create_models_from_scraping(self, scraping_batch):
        yield from (
            user_models.get(self.user)(
                id=data.id,
                cashtags=data.cashtags,
                content=data.content,
                conversation_id=data.conversationId,
                coordinates=data.coordinates,
                tweeted_at=data.date,
                hashtags=data.hashtags,
                in_reply_to_tweet_id=data.inReplyToTweetId,
                in_reply_to_user=self.check_reply(data.inReplyToUser),
                language=data.lang,
                like_count=data.likeCount,
                mentioned_users=self.check_mentioned(data.mentionedUsers),
                outlinks=self.check_outlinks(data.outlinks),
                place=data.place,
                quote_count=data.quoteCount,
                quoted_tweet=self.check_quoted_tweet(data.quotedTweet),
                reply_count=data.replyCount,
                retweet_count=data.retweetCount,
                retweeted_tweet=data.retweetedTweet,
                source=data.source,
                source_url=data.sourceUrl,
                url=data.url,
                user_name=data.user.username,
            )
            for data in scraping_batch
        )

    def load_scraped_data(self, scraped_batch, engine: Engine):
        with Session(engine) as sess:
            for fixture in self.create_models_from_scraping(scraping_batch=scraped_batch):
                sess.add(fixture)
                sess.commit()

        last_scraped = self.get_newest_scraped_tweet()
        if last_scraped is None:
            return None
        return str(last_scraped.tweeted_at).replace(" ", "-")


class TwitterNewsScraper(TwitterScraperBase):
    def __init__(self, user: str, database_session: Session, last_scraped_tweet: str):
        super().__init__(user, database_session)
        self.last_scraped_tweet = datetime.fromisoformat(last_scraped_tweet)

    def set_query_time_from_last_scraped(self):
        scraper_time = int(self.last_scraped_tweet.timestamp()) + 7201
        self.query_time = f'since_time:{scraper_time}'
        logger.warning(f'New tweets for the user : {self.user} will be scraped from : {self.last_scraped_tweet}')
        return self.query_time

    def scraping_data_news(self, until_day=1):
        if self.last_scraped_tweet:
            since_time = self.set_query_time_from_last_scraped()
        else:
            raise NewsScraperMissConfigured(f"Check the fingerprint file for the user : {self.user}")

        day_in_timestamp = 86400
        until_time = int(time.time() - (day_in_timestamp * until_day))
        logger.warning(f'until_time : {datetime.utcfromtimestamp(until_time).strftime("%Y-%m-%d %H:%M:%S")}')
        query = f'from:{self.user} {since_time} until_time:{until_time}'
        logger.warning(f'The search query is : {query}')
        yield from self.start_scraping(query)


class TwitterHistoryScraper(TwitterScraperBase):

    def __init__(self, user: str, database_session: Session):
        super().__init__(user, database_session)

    def set_query_time_until_last_scraped(self):
        last_record_time = self.get_last_scraped_tweet().tweeted_at
        logger.warning(f'{self.user} will be scraped from the far far away until: {last_record_time}')
        self.query_time = f'until_time:{last_record_time.timestamp()}'
        return self.query_time

    def set_query_for_history_scraper(self):
        if self.get_last_scraped_tweet():
            scraper_time = self.set_query_time_until_last_scraped()
        else:
            scraper_time = self.since_time_str
            logger.warning(f'{self.user} will be scraped from the far far away until the previous day')

        day_in_timestamp = 86400
        until_time = int(time.time() - (day_in_timestamp * 1))
        query = f'from:{self.user} {scraper_time[:-2]} until_time:{until_time}'
        logger.warning(f'The search query is : {query}')
        yield from self.start_scraping(query)


def scraping_data_from_hashtag():
    max_item = sntwitter.TwitterHashtagScraper('bitcoin').get_items()
    preprocess = sorted(
        max_item, key=lambda x: x.replyCount > 10 and x.retweetCount > 10 and x.likeCount > 10
    )
    for tweet in preprocess:
        yield tweet


if __name__ == '__main__':
    postgres_engine: Engine = connect_database_sqlalchemy()
    scraping_type = 'news'
    twitter_user = 'JoeBiden'
    user_models.get(twitter_user).metadata.create_all(postgres_engine)
    with Session(postgres_engine) as session:
        if scraping_type == 'news':
            scraper = TwitterNewsScraper(user=twitter_user, database_session=session,
                                         last_scraped_tweet='2022-04-22 17:06:01')
            batch = scraper.scraping_data_news()
        else:
            scraper = TwitterHistoryScraper(user=twitter_user, database_session=session)
            batch = scraper.set_query_for_history_scraper()

    last_tweeted_at = scraper.load_scraped_data(engine=postgres_engine, scraped_batch=batch)
    df = pd.read_sql(
        """
        select * from joe_biden
        """,
        postgres_engine
    )

    df.to_parquet(path=f'{twitter_user}_{last_tweeted_at}.pq', compression='snappy')

# pylint:disable=missing-function-docstring, missing-module-docstring
# pylint:disable=import-error
import logging
import time
from datetime import datetime

import snscrape.modules.twitter as sntwitter
from playhouse.shortcuts import model_to_dict

from orm.models import (
    TwitterDataModelElonMusk,
    TwitterDataModelJeffBezos,
    TwitterDataModelBarackObama,
    TwitterDataModelJoeBiden,
    TwitterDataModelKamalaHarris, mysql_db
)
from scraper.context import init_database_local
from scraper.custom_exceptions import UserModelNotFound

user_models = {
    'elonmusk': TwitterDataModelElonMusk,
    'JeffBezos': TwitterDataModelJeffBezos,
    'BarackObama': TwitterDataModelBarackObama,
    'JoeBiden': TwitterDataModelJoeBiden,
    'KamalaHarris': TwitterDataModelKamalaHarris,
}


class TwitterScraperConfig:

    def __init__(self, user: str):
        self.user = user
        self.query_time = None
        self.since_time_str = 'since_time:964381815'
        self.since_time_int = 964381815
        self.time_delta = 3
        self.logger = logging.getLogger(__name__)


class TwitterScraper(TwitterScraperConfig):

    def __init__(self, user: str, scraping_type: str):
        super().__init__(user)
        self.user = user
        self.query_time = None
        self.scraping_type = scraping_type

    def validate_user_model(self):
        if self.user not in user_models:
            raise UserModelNotFound(self.user)

    @property
    def get_last_scraped_tweet(self):
        return user_models.get(self.user).get_oldest_elem_from_table()

    def set_query_time_until_last_scraped(self):
        self.logger.info(f'Old tweets for the user: {self.user} '
                         f'will be scraped from: {datetime.now()}')
        last_record_time = datetime.strptime(str(self.get_last_scraped_tweet.created_at), "%Y-%m-%d %H:%M:%S")
        self.logger.info(f'The until_time variable is : {self.query_time}')
        self.query_time = f'until_time:{last_record_time.timestamp()}'
        return self.query_time

    def set_query_time_from_last_scraped(self):
        last_record_time = datetime.strptime(str(self.get_last_scraped_tweet.created_at), "%Y-%m-%d %H:%M:%S")
        scraper_time = int(last_record_time.timestamp()) + 1
        self.query_time = f'since_time:{scraper_time}'
        self.logger.info(f'New tweets for the user: {self.user} will be scraped from: {self.query_time}')
        self.logger.info(f'The until_time variable is : {self.query_time}')
        return self.query_time

    def scraping_data_history(self):
        if self.get_last_scraped_tweet:
            scraper_time = self.set_query_time_until_last_scraped()
        else:
            scraper_time = self.since_time_str

        query = f'from:{self.user} {scraper_time[:-2]}'
        self.logger.info(f'The search query is : {query}')
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
        self.logger.info(f'The search query is : {query}')
        tweets = sntwitter.TwitterSearchScraper(query).get_items()
        for tweet in tweets:
            if tweet:
                yield tweet
            else:
                self.logger.warning('Need to wait more time! At least 3 day after the last tweet')

    def create_models_from_scraping(self, scraping_type, twitter_user):
        if scraping_type == 'since':
            scraping_batch = self.scraping_data_news()
        else:
            scraping_batch = self.scraping_data_history()

        yield from (
            user_models.get(twitter_user)(
                cashtags=data.cashtags,
                content=data.content,
                conversation_id=data.conversationId,
                coordinates=data.coordinates,
                tweeted_at=data.date,
                hashtags=data.hashtags,
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


def scraping_data_from_hashtag():
    max_item = sntwitter.TwitterHashtagScraper('bitcoin').get_items()
    preprocess = sorted(
        max_item, key=lambda x: x.replyCount > 10 and x.retweetCount > 10 and x.likeCount > 10
    )
    for tweet in preprocess:
        yield tweet


def apply_all_fixture(scraping_type, twitter_user):
    scraper = TwitterScraper(user=twitter_user, scraping_type=scraping_type)
    for fixture in scraper.create_models_from_scraping(scraping_type=scraping_type, twitter_user=twitter_user):
        data = model_to_dict(fixture, recurse=False)
        fixture.insert(data).on_conflict(update=data).execute()


if __name__ == '__main__':
    init_database_local(database='twitter')
    mysql_db.create_tables([TwitterDataModelJeffBezos])
    apply_all_fixture(scraping_type='old', twitter_user='JeffBezos')

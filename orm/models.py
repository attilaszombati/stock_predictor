# pylint:disable=missing-function-docstring, missing-module-docstring, missing-class-docstring
import logging

from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import INTEGER
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()


class TwitterBaseModel(Base):
    __tablename__ = 'base'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cashtags = Column(String(255), index=True, nullable=True)
    content = Column(String(255))
    conversation_id = Column(INTEGER())
    coordinates = Column(String(255), nullable=True)
    tweeted_at = Column(DateTime)
    hastags = Column(String(255), nullable=True)
    in_reply_to_tweet_id = Column(Integer, nullable=True)
    in_reply_to_user = Column(String(255), nullable=True)
    language = Column(String(255))
    like_count = Column(INTEGER(), nullable=True)
    mentioned_users = Column(String(255))
    outlinks = Column(String(255), nullable=True)
    place = Column(String(255), nullable=True)
    quote_count = Column(INTEGER())
    quoted_tweet = Column(Boolean, nullable=True)
    reply_count = Column(INTEGER(), nullable=True)
    retweet_count = Column(INTEGER(), nullable=True)
    retweeted_tweet = Column(Boolean, nullable=True)
    source = Column(String(255))
    source_url = Column(String(255))
    url = Column(String(255))
    user_name = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    __mapper_args__ = {'eager_defaults': True}

    @classmethod
    def get_latest_elem_from_table(cls):
        try:
            last_elem = cls.select(cls).order_by(cls.created_at.desc()).get()
        except NoResultFound:
            return None
        else:
            print(f'The latest tweet has been created at: {last_elem.created_at}')
            return last_elem

    @classmethod
    def get_oldest_elem_from_table(cls):
        try:
            last_elem = cls.select(cls).order_by(cls.created_at.asc()).get()
        except NoResultFound:
            return None
        else:
            print(f'The oldest tweet has been created at: {last_elem.created_at}')
            return last_elem


class TwitterDataModelElonMusk(TwitterBaseModel):
    __tablename__ = 'elon_musk'


class TwitterDataModelJeffBezos(TwitterBaseModel):
    __tablename__ = 'jeff_bezos'


class TwitterDataModelBarackObama(TwitterBaseModel):
    __tablename__ = 'barack_obama'


class TwitterDataModelJoeBiden(TwitterBaseModel):
    __tablename__ = 'joe_biden'


class TwitterDataModelKamalaHarris(TwitterBaseModel):
    __tablename__ = 'kamala_harris'


class RedditDataModel(Base):
    # pylint:disable=too-few-public-methods
    __tablename__ = 'wallstreetbets'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    author = Column(String(255), nullable=True)
    posted_at = Column(DateTime)
    post_id = Column(INTEGER, nullable=False)
    self_text = Column(String(255), nullable=True)
    subreddit = Column(String(255))
    url = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    title = Column(String(255))

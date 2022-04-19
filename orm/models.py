# pylint:disable=no-name-in-module
import logging

from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import INTEGER, BIGINT
from sqlalchemy.orm import declarative_base, Session

logger = logging.getLogger(__name__)

Base = declarative_base()


class TwitterBaseModel(Base):
    __abstract__ = True

    id = Column(BIGINT(), primary_key=True, index=True, autoincrement=True)
    cashtags = Column(String(1000), index=True, nullable=True)
    content = Column(String(1000))
    conversation_id = Column(BigInteger())
    coordinates = Column(String(1000), nullable=True)
    tweeted_at = Column(DateTime)
    hashtags = Column(String(1000), nullable=True)
    in_reply_to_tweet_id = Column(BigInteger(), nullable=True)
    in_reply_to_user = Column(String(1000), nullable=True)
    language = Column(String(1000))
    like_count = Column(BigInteger(), nullable=True)
    mentioned_users = Column(String(1000))
    outlinks = Column(String(1000), nullable=True)
    place = Column(String(1000), nullable=True)
    quote_count = Column(BigInteger())
    quoted_tweet = Column(String(1000), nullable=True)
    reply_count = Column(BigInteger(), nullable=True)
    retweet_count = Column(BigInteger(), nullable=True)
    retweeted_tweet = Column(String(1000), nullable=True)
    source = Column(String(1000))
    source_url = Column(String(1000))
    url = Column(String(1000))
    user_name = Column(String(1000))
    created_at = Column(DateTime, server_default=func.now())

    __mapper_args__ = {'eager_defaults': True}

    @classmethod
    def get_latest_elem_from_table(cls, session: Session):
        last_elem = select(cls).order_by(cls.tweeted_at.desc())
        res = session.execute(last_elem).scalars().first()
        if not res:
            return None
        return res

    @classmethod
    def get_oldest_elem_from_table(cls, session: Session):
        last_elem = select(cls).order_by(cls.tweeted_at.asc())
        res = session.execute(last_elem).scalars().first()
        if not res:
            return None
        return res


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
    author = Column(String(1000), nullable=True)
    posted_at = Column(DateTime)
    post_id = Column(INTEGER, nullable=False)
    self_text = Column(String(1000), nullable=True)
    subreddit = Column(String(1000))
    url = Column(String(1000))
    created_at = Column(DateTime, server_default=func.now())
    title = Column(String(1000))

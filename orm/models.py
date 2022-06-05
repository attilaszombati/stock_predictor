import logging

from sqlalchemy import Column, Integer, func
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import INTEGER, VARCHAR, DATETIME
from sqlalchemy.orm import declarative_base, Session

logger = logging.getLogger(__name__)

Base = declarative_base()


class TwitterBaseModel(Base):
    __abstract__ = True

    id = Column(INTEGER(), primary_key=True, index=True, autoincrement=True)
    cashtags = Column(VARCHAR(1000), index=True, nullable=True)
    content = Column(VARCHAR(1000))
    conversation_id = Column(INTEGER())
    coordinates = Column(VARCHAR(1000), nullable=True)
    tweeted_at = Column(DATETIME)
    hashtags = Column(VARCHAR(1000), nullable=True)
    in_reply_to_tweet_id = Column(INTEGER(), nullable=True)
    in_reply_to_user = Column(VARCHAR(1000), nullable=True)
    language = Column(VARCHAR(1000))
    like_count = Column(INTEGER(), nullable=True)
    mentioned_users = Column(VARCHAR(1000))
    outlinks = Column(VARCHAR(1000), nullable=True)
    place = Column(VARCHAR(1000), nullable=True)
    quote_count = Column(INTEGER())
    quoted_tweet = Column(VARCHAR(1000), nullable=True)
    reply_count = Column(INTEGER(), nullable=True)
    retweet_count = Column(INTEGER(), nullable=True)
    retweeted_tweet = Column(VARCHAR(1000), nullable=True)
    source = Column(VARCHAR(1000))
    source_url = Column(VARCHAR(1000))
    url = Column(VARCHAR(1000))
    user_name = Column(VARCHAR(1000))
    created_at = Column(DATETIME, server_default=func.now())

    __mapper_args__ = {'eager_defaults': True}

    @classmethod
    def get_newest_tweeted_at_elem(cls, session: Session):
        last_elem = select(cls).order_by(cls.tweeted_at.desc())
        res = session.execute(last_elem).scalars().first()
        if not res:
            return None
        return res

    @classmethod
    def get_oldest_tweeted_at_elem(cls, session: Session):
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
    __tablename__ = 'wallstreetbets'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    author = Column(VARCHAR(1000), nullable=True)
    posted_at = Column(DATETIME)
    post_id = Column(INTEGER, nullable=False)
    self_text = Column(VARCHAR(1000), nullable=True)
    subreddit = Column(VARCHAR(1000))
    url = Column(VARCHAR(1000))
    created_at = Column(DATETIME, server_default=func.now())
    title = Column(VARCHAR(1000))

    @classmethod
    def get_newest_reddit_elem(cls, session: Session):
        last_elem = select(cls).order_by(cls.tweeted_at.desc())
        res = session.execute(last_elem).scalars().first()
        if not res:
            return None
        return res

    @classmethod
    def get_oldest_reddit_elem(cls, session: Session):
        last_elem = select(cls).order_by(cls.tweeted_at.asc())
        res = session.execute(last_elem).scalars().first()
        if not res:
            return None
        return res


class RedditOfficialApiModel(Base):
    __tablename__ = 'wallstreetbets_official_api'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    author = Column(VARCHAR(1000), nullable=True)
    title = Column(VARCHAR(1000))
    score = Column(INTEGER, nullable=False)
    num_comments = Column(INTEGER, nullable=False)
    self_text = Column(VARCHAR(1000), nullable=True)
    posted_at = Column(DATETIME)
    total_awards_received = Column(INTEGER, nullable=False)
    scraped_at = Column(DATETIME, server_default=func.now())
    view_count = Column(VARCHAR(1000), nullable=True)
    post_id = Column(INTEGER, nullable=False)
    subreddit = Column(VARCHAR(1000))
    subreddit_id = Column(INTEGER, nullable=False)
    url = Column(VARCHAR(1000))
    # upvote = IntegerField()
    # upvote_ratio = IntegerField()

    @classmethod
    def get_newest_reddit_elem(cls, session: Session):
        last_elem = select(cls).order_by(cls.posted_at.desc())
        res = session.execute(last_elem).scalars().first()
        if not res:
            return None
        return res

    @classmethod
    def get_oldest_reddit_elem(cls, session: Session):
        last_elem = select(cls).order_by(cls.posted_at.asc())
        res = session.execute(last_elem).scalars().first()
        if not res:
            return None
        return res

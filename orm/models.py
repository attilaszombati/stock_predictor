# pylint:disable=missing-function-docstring, missing-module-docstring, missing-class-docstring
import datetime
import logging
from typing import Any

from peewee import (
    Model,
    fn,
    IntegrityError,
    ModelBase,
    DateTimeField,
    CharField,
    IntegerField,
    DoesNotExist,
    BooleanField,
)
from playhouse.shortcuts import model_to_dict

from scraper.context import get_mysql_db_local

mysql_db = get_mysql_db_local()

logger = logging.getLogger(__name__)


class BaseModel(Model):
    # pylint: disable=no-member
    @classmethod
    def table_name(cls) -> str:
        return cls._meta.table_name

    # pylint: disable=no-member
    @classmethod
    def bulk_create_mysql(cls, model_list, batch_size=1000):
        rows = [model_to_dict(model, recurse=False) for model in model_list]
        models = []

        for index in range(0, len(rows), batch_size):
            rows_batch = rows[index: index + batch_size]
            # pylint: disable=no-value-for-parameter
            cls.insert_many(rows_batch).execute()

            newly_created = list(cls.select().where(cls._meta.primary_key >= fn.last_insert_id()))
            if len(newly_created) != len(rows_batch):
                raise ValueError(
                    f'The newly created record count ({len(newly_created)})'
                    f' does not match with the '
                    f'record count sent to the DB ({len(rows_batch)})'
                )
            models.extend(newly_created)

        return models

    # pylint: disable=no-member
    @classmethod
    def create_table(cls, safe=True, **kwargs):  # pylint: disable=arguments-differ
        try:
            comment_literal = f'COMMENT="{cls._meta.comment}"'

            if cls._meta.table_settings is None:
                cls._meta.table_settings = [comment_literal]
            else:
                cls._meta.table_settings.append(comment_literal)
        except AttributeError:
            pass

        return super().create_table(safe, **kwargs)

    class Meta:
        # pylint:disable=too-few-public-methods
        legacy_table_names = False

    # pylint:disable=logging-fstring-interpolation
    def insert_if_not_exists(self) -> bool:
        """
        Try to insert the item in the database.
        Only inserts if it its not exists by PK.
        :return: True if item was inserted, false if wasn't
        """
        try:
            self.save(force_insert=True)
        except IntegrityError as err:
            error_message = err.args[1]
            if 'Duplicate entry' in error_message:
                logger.debug(
                    f'not inserted: {self._meta.table_name} {model_to_dict(self, max_depth=0)}'
                )
            else:
                raise err
            return False
        except Exception as err:  # pylint: disable=broad-except
            logger.warning(
                f'Couldn\'t insert: {self._meta.table_name}'
                f' {model_to_dict(self, max_depth=0)}|\n{err}'
            )
            return False
        return True

    @classmethod
    def create_add_to_models_meta_class(cls, table_name) -> type:
        class AddToModels(ModelBase):
            def __new__(cls, name, bases, attrs) -> Any:
                new_cls = super().__new__(cls, name, bases, attrs)
                meta = attrs.pop('Meta', None)
                if meta is not None:
                    meta.table_name = table_name
                return new_cls

        return AddToModels


class TwitterBaseModel(BaseModel):
    cashtags = CharField(null=True)
    content = CharField()
    conversation_id = IntegerField()
    coordinates = CharField(null=True)
    tweeted_at = DateTimeField()
    hashtags = CharField(null=True)
    in_reply_to_tweet_id = IntegerField(null=True)
    in_reply_to_user = CharField(null=True)
    language = CharField()
    like_count = IntegerField(null=True)
    mentioned_users = CharField
    outlinks = CharField(null=True)
    place = CharField(null=True)
    quote_count = IntegerField()
    quoted_tweet = BooleanField(null=True)
    reply_count = IntegerField(null=True)
    retweet_count = IntegerField(null=True)
    retweeted_tweet = BooleanField(null=True)
    source = CharField()
    source_url = CharField()
    url = CharField()
    user_name = CharField()
    created_at = DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    class Meta:
        # pylint:disable=too-few-public-methods
        database = mysql_db

    @classmethod
    def get_latest_elem_from_table(cls):
        try:
            last_elem = cls.select(cls).order_by(cls.created_at.desc()).get()
        except DoesNotExist:
            return None
        else:
            print(f'The latest tweet has been created at: {last_elem.created_at}')
            return last_elem

    @classmethod
    def get_oldest_elem_from_table(cls):
        try:
            last_elem = cls.select(cls).order_by(cls.created_at.asc()).get()
        except DoesNotExist:
            return None
        else:
            print(f'The oldest tweet has been created at: {last_elem.created_at}')
            return last_elem


class TwitterDataModelElonMusk(TwitterBaseModel):
    # pylint: disable=too-few-public-methods
    class Meta:
        table_name = 'elon_musk'


class TwitterDataModelJeffBezos(TwitterBaseModel):
    # pylint: disable=too-few-public-methods
    class Meta:
        table_name = 'jeff_bezos'


class TwitterDataModelBarackObama(TwitterBaseModel):
    # pylint: disable=too-few-public-methods
    class Meta:
        table_name = 'barack_obama'


class TwitterDataModelJoeBiden(TwitterBaseModel):
    # pylint: disable=too-few-public-methods
    class Meta:
        table_name = 'joe_biden'


class TwitterDataModelKamalaHarris(TwitterBaseModel):
    # pylint: disable=too-few-public-methods
    class Meta:
        table_name = 'kamala_harris'


class RedditDataModel(BaseModel):
    author = CharField(null=True)
    created_at = DateTimeField(primary_key=True)
    post_id = IntegerField(null=False)
    # link = CharField()
    self_text = CharField(null=True)
    subreddit = CharField()
    url = CharField()
    scraped_at = DateTimeField(default=datetime.datetime.now)
    title = CharField()

    class Meta:
        # pylint:disable=too-few-public-methods
        database = mysql_db
        table_name = 'wallstreetbets'


class RedditOfficialApiModel(BaseModel):
    author = CharField(null=True)
    title = CharField()
    score = IntegerField()
    num_comments = IntegerField()
    self_text = CharField(null=True)
    created_at = DateTimeField(primary_key=True)
    total_awards_received = IntegerField()
    scraped_at = DateTimeField(default=datetime.datetime.now)
    view_count = IntegerField(null=True)
    post_id = CharField()
    subreddit = CharField()
    subreddit_id = IntegerField()
    url = CharField()

    # upvote = IntegerField()
    # upvote_ratio = IntegerField()

    class Meta:
        # pylint:disable=too-few-public-methods
        database = mysql_db
        table_name = 'wallstreetbets_official_api'

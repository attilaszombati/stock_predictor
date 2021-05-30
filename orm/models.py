import datetime
import logging
from typing import List, Any

from peewee import Model, fn, IntegrityError, ModelBase, MySQLDatabase, DateTimeField, CharField, IntegerField, \
    BooleanField
from playhouse.shortcuts import model_to_dict

logger = logging.getLogger(__name__)

mysql_db = MySQLDatabase(user='root', password='',
                         host='localhost', port=3306, database='reddit')


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
                    f'The newly created record count ({len(newly_created)}) does not match with the '
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
        legacy_table_names = False

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
                f'Couldn\'t insert: {self._meta.table_name} {model_to_dict(self, max_depth=0)}|\n{err}'
            )
            return False
        return True


def create_add_to_models_meta_class(model_list: List[BaseModel]) -> type:
    class AddToModels(ModelBase):
        def __new__(mcs, name, bases, attrs) -> Any:
            new_cls = super().__new__(mcs, name, bases, attrs)
            if attrs.get('skip_from_models_list') is not True:
                model_list.append(new_cls)
            return new_cls

    return AddToModels


class TwitterDataModel(BaseModel):
    url = CharField()
    # scraped_at = DateTimeField()
    # content = CharField()
    # renderedContent = CharField()
    # content_id = IntegerField(null=False)
    user_name = CharField()
    # display_name = CharField()
    # user_id = IntegerField(null=False)
    # description = CharField()
    # raw_description = CharField()
    # verified = BooleanField()
    created_at = DateTimeField()
    # followers_count = IntegerField(null=False)
    # friends_count = IntegerField(null=False)
    # statuses_count = IntegerField(null=False)
    # favourites_count = IntegerField(null=False)
    # listed_count = IntegerField(null=False)
    # media_count = IntegerField(null=False)
    # location = CharField()
    # protected = BooleanField()
    # linkUrl = CharField()
    # profile_image_url = CharField()
    # profile_banner_url = CharField()
    reply_count = IntegerField(null=False)
    retweet_count = IntegerField(null=False)
    like_count = IntegerField(null=False)
    # quote_count = IntegerField(null=False)
    # conversation_id = IntegerField(null=False)
    # id = None

    class Meta:
        database = mysql_db
        table_name = 'bitcoin'

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
        database = mysql_db
        table_name = 'wallstreetbets_official_api'

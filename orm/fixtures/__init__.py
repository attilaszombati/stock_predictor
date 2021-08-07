# pylint:disable=missing-function-docstring, missing-module-docstring
from playhouse.shortcuts import model_to_dict
from scraper.twitter import create_models_from_scraping as twitter_data


def apply_all_fixture():
    for fixture in twitter_data():
        data = model_to_dict(fixture, recurse=False)
        fixture.insert(data).on_conflict(update=data).execute()

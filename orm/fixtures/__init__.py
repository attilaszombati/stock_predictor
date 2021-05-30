from playhouse.shortcuts import model_to_dict
from .twitter import create_models_from_scraping as twitter_data

def apply_all_fixture():
    for f in twitter_data():
        data = model_to_dict(f, recurse=False)
        f.insert(data).on_conflict(update=data).execute()
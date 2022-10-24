# pylint:disable=no-name-in-module, unexpected-keyword-arg
import os

from flask import Flask, request
from tensorflow import keras
import logging

app = Flask(__name__)
logger = logging.getLogger('twitter-scraper')


def main(data):
    logger.warning(f"Input data is : {data}")
    get_model_from_gcs = keras.models.load_model('gs://stock_predictor_bucket/my_model')
    logger.warning(f"Model is : {get_model_from_gcs}")
    return get_model_from_gcs.predict(data)


@app.route("/", methods=['POST'])
def handler():
    data = request.get_json()
    print(data)
    twitter_data = data.get('TWITTER_POST_DATA', [])
    prediction = main(data=twitter_data)
    return {'prediction': prediction}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

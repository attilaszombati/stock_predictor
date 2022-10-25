# pylint:disable=no-name-in-module, unexpected-keyword-arg
import os

import numpy as np
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


def convert_to_np_array(twitter_data):
    convert = [twitter_data]
    return np.asarray(convert)


@app.route("/", methods=['POST'])
def handler():
    data = request.get_json()
    print(data)
    twitter_data = data.get('TWITTER_POST_DATA', [])
    data = convert_to_np_array(twitter_data)
    prediction = main(data=data)
    return {'prediction': prediction.item(0)}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# pylint:disable=no-name-in-module, unexpected-keyword-arg
import os

from google.cloud import bigquery
import numpy as np
from flask import Flask, request
from tensorflow import keras
import logging

from utils.cloud_storage import CloudStorageUtils

app = Flask(__name__)
logger = logging.getLogger('twitter-scraper')

PREDICTOR_BUCKET = 'stock_predictor_bucket'
MODEL_NAME = 'TSLA_ELON_MUSK'


def main(data, predictor_version: str):
    logger.warning(f"Input data is : {data}")
    get_model_from_gcs = keras.models.load_model(f'gs://{PREDICTOR_BUCKET}/{MODEL_NAME}_{predictor_version}')
    logger.warning(f"Model is : {get_model_from_gcs}")
    predicted_data = get_model_from_gcs.predict(data)
    return predicted_data


def convert_to_np_array(twitter_data):
    convert = [twitter_data]
    return np.asarray(convert)


def convert_input_to_lstm_format(dataframe):
    FEATURE_START_INDEX = 8
    DATES_COLUMN = 0

    df_as_np = dataframe.to_numpy()

    dates = df_as_np[:, DATES_COLUMN]

    middle_matrix = df_as_np[:, FEATURE_START_INDEX:-1]
    features = middle_matrix.reshape((len(dates), middle_matrix.shape[1], 1)).astype(np.float32)
    logger.warning(f"Features are : {features}")
    return features


def get_data_from_big_query():
    client = bigquery.Client(project='attila-szombati-sandbox', location='us-central1')

    query = """
        SELECT 
          tweeted_at
          , close
          , diff_after_1_day
          , diff_after_2_day
          , diff_after_3_day
          , diff_after_4_day
          , diff_after_5_day
          , diff_after_6_day
          , diff_after_7_day
          , aggregated_sentiment_compoun
          , aggregated_sentiment_neg
          , aggregated_sentiment_neu
          , aggregated_sentiment_pos
          , aggregated_in_reply_to_user
          , aggregated_like_count
          , aggregated_quote_count
          , aggregated_reply_count
          , aggregated_retweet_count
        FROM `attila-szombati-sandbox.cl_layer_us.elon_musk_tsla`
        ORDER BY tweeted_at DESC
        LIMIT 1
    """

    query_job = client.query(query)
    df = query_job.to_dataframe()

    logger.warning(f"Dataframe is : {df}")

    return df


@app.route("/", methods=['POST'])
def handler():
    storage = CloudStorageUtils()
    data = request.get_json()
    logger.warning(f'Input data is: {data}')
    predictor_version = data.get('PREDICTOR_VERSION', 'latest')
    if predictor_version == 'latest':
        predictor_version = storage.get_fingerprint_for_user(bucket_name=PREDICTOR_BUCKET,
                                                             file_name='latest_version.csv')
    twitter_data_df = get_data_from_big_query()
    input_dataset = convert_input_to_lstm_format(twitter_data_df)
    prediction = main(data=input_dataset, predictor_version=predictor_version)
    logger.warning(f'The predicted data is : {prediction.item(0)}')
    return {'prediction': prediction.item(0)}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

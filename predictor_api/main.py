# pylint:disable=no-name-in-module, unexpected-keyword-arg, invalid-name, too-many-locals
import logging
import os

import numpy as np
from alpaca.trading import (
    MarketOrderRequest,
    TimeInForce,
    TradingClient
)
from alpaca.trading.enums import OrderSide
from flask import Flask, request
from google.cloud import bigquery
from tensorflow import keras

from utils.cloud_storage import CloudStorageUtils

app = Flask(__name__)
logger = logging.getLogger("twitter-scraper")

PREDICTOR_BUCKET = "stock_predictor_bucket"
MODEL_NAME = "TSLA_ELON_MUSK"


def main(data, predictor_version: str):
    logger.warning(f"Input data is : {data}")
    get_model_from_gcs = keras.models.load_model(
        f"gs://{PREDICTOR_BUCKET}/{MODEL_NAME}_{predictor_version}"
    )
    logger.warning(f"Model is : {get_model_from_gcs}")
    predicted_data = get_model_from_gcs.predict(data)
    return predicted_data


def convert_to_np_array(twitter_data):
    convert = [twitter_data]
    return np.asarray(convert)


def convert_input_to_lstm_format(dataframe):
    FEATURE_START_INDEX = 2
    DATES_COLUMN = 0

    df_as_np = dataframe.to_numpy()

    dates = df_as_np[:, DATES_COLUMN]

    middle_matrix = df_as_np[:, FEATURE_START_INDEX:-1]
    features = middle_matrix.reshape((len(dates), middle_matrix.shape[1], 1)).astype(
        np.float32
    )
    logger.warning(f"Features are : {features}")
    return features


def get_data_from_big_query():
    client = bigquery.Client(project="attila-szombati-sandbox", location="us-central1")

    query = """
        SELECT 
          tweeted_at
          , close
          , diff_after_1_day
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
        WHERE DATE_DIFF(CURRENT_DATE(), tweeted_at, DAY) = 1
    """

    query_job = client.query(query)
    df = query_job.to_dataframe()

    logger.warning(f"Dataframe is : {df}")

    return df


@app.route("/", methods=["POST"])
def handler():
    storage = CloudStorageUtils()
    data = request.get_json()
    logger.warning(f"Input data is: {data}")
    predictor_version = data.get("PREDICTOR_VERSION", "latest")
    if predictor_version == "latest":
        predictor_version = storage.get_fingerprint_for_user(
            bucket_name=PREDICTOR_BUCKET, file_name="latest_version.csv"
        )
    twitter_data_df = get_data_from_big_query()
    if twitter_data_df.empty:
        return "No data to predict, next prediction will be in 24 hours"
    input_dataset = convert_input_to_lstm_format(twitter_data_df)
    prediction = main(data=input_dataset, predictor_version=predictor_version)
    logger.warning(f"The predicted data is : {prediction.item(0)}")

    money = [1000]

    prev_day_close = twitter_data_df["close"].iloc[0]
    logger.warning(f"Previous day close is : {prev_day_close}")

    api = TradingClient(
        "PKM7L9DOBVFYTY56MJPR",
        "dd8eB5zL3YOQuLveUL2fw34gXA8vur80AkV1yV14",
        url_override="https://paper-api.alpaca.markets",
    )

    positions = api.get_all_positions()

    buy_orders = [pos for pos in positions if pos.side == 'long']
    sell_orders = [pos for pos in positions if pos.side == 'short']

    if prediction.item(0) > prev_day_close:
        logger.warning("Prediction is higher than previous day close")

        if len(buy_orders) == 0:
            logger.warning("No open orders, creating one")
            market_order_data = MarketOrderRequest(
                symbol="BTC/USD",
                notional=money[-1],
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC,
            )
        elif len(sell_orders) == 1:
            logger.warning("There are open sell orders, cancelling them")
            position = api.get_all_positions()
            new_money = position[0].market_value
            money.append(new_money)
            api.close_all_positions(cancel_orders=True)
            market_order_data = MarketOrderRequest(
                symbol="BTC/USD",
                notional=money[-1],
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC,
            )
        else:
            logger.warning("There are open buy orders, doing nothing")
    else:
        logger.warning("Prediction is lower than previous day close")

        if len(sell_orders) == 0:
            logger.warning("No open orders, creating one")
            market_order_data = MarketOrderRequest(
                symbol="BTC/USD",
                notional=money[-1],
                side=OrderSide.SELL,
                time_in_force=TimeInForce.GTC,
            )
        elif len(buy_orders) == 1:
            logger.warning("There are open buy orders, cancelling them")
            position = api.get_all_positions()
            new_money = position[0].market_value
            money.append(new_money)
            api.close_all_positions(cancel_orders=True)
            market_order_data = MarketOrderRequest(
                symbol="BTC/USD",
                notional=money[-1],
                side=OrderSide.SELL,
                time_in_force=TimeInForce.GTC,
            )
        else:
            logger.warning("There are open sell orders, doing nothing")

    api.submit_order(order_data=market_order_data)

    logger.warning(f"Money is : {money}")

    return {"prediction": prediction.item(0)}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

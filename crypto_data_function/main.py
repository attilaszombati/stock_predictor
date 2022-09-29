import logging
import os
from datetime import datetime

import pandas as pd
import yfinance as yf
from alpaca.data import TimeFrame
from alpaca_trade_api import REST
from flask import Flask, request

from utils.cloud_storage import CloudStorageUtils

logger = logging.getLogger('twitter-scraper')

app = Flask(__name__)

API_KEY = 'AKRKQK0FZP17RH0TS516'
SECRET_KEY = 'GszzkYig0nXUMquNyz0Viw1R95oiSKi0KjJOcz4C'


def main(symbol: str = 'BTCUSD'):
    gcs_storage = CloudStorageUtils()
    alpaca_api = REST(API_KEY, SECRET_KEY, api_version='v2')
    time_frame = TimeFrame.Minute
    data = alpaca_api.get_crypto_bars(
        symbol=symbol,
        timeframe=time_frame.value
    ).df.iloc[[-1]]
    latest_bar_data = data.index.format()[0].replace(" ", "_")
    data.to_parquet(path=f'/tmp/{latest_bar_data}_{symbol}.pq', compression='snappy')
    logger.warning(f"Saving {latest_bar_data} data for {symbol} to cloud storage")

    gcs_storage.save_data_to_cloud_storage(bucket_name='crypto_data_collection',
                                           file_name=f'{symbol}/{latest_bar_data}_{symbol}.pq',
                                           parquet_file=f'/tmp/{latest_bar_data}_{symbol}.pq')

    return latest_bar_data


def historical_data(symbol: str = 'BTC-USD'):
    gcs_storage = CloudStorageUtils()

    freq = '-7d'
    dates = pd.date_range(start=datetime.now().date().strftime('%Y-%m-%d'), periods=670, freq=freq,
                          inclusive=None).strftime('%Y-%m-%d').to_list()

    shift_dates = [[i, j] for i, j in zip(dates, dates[1:])]

    for one_week in shift_dates:
        data = yf.download(symbol, start=one_week[1], end=one_week[0], interval="1m", actions=True)
        data.rename(columns=str.lower, inplace=True)
        data.index.rename("timestamp", inplace=True)
        latest_bar_data = data.index.format()[0].replace(" ", "_")

        data.to_parquet(path=f'/tmp/{latest_bar_data}_{symbol}.pq', compression='snappy')

        logger.warning(f"Saving historical data for {symbol} to cloud storage for the week {one_week}")

        gcs_storage.save_data_to_cloud_storage(bucket_name='crypto_data_collection',
                                               file_name=f'{symbol}/{latest_bar_data}_{symbol}.pq',
                                               parquet_file=f'/tmp/{latest_bar_data}_{symbol}.pq')



@app.route("/", methods=['POST'])
def handler():
    data = request.get_json()
    logger.warning(f"The data is : {data}")
    symbols = data.get('SYMBOLS')

    for symbol in symbols:
        if data.get('SCRAPING_TYPE') == 'history':
            historical_data(symbol=symbol)
        else:
            main(symbol=symbol)

    return "OK"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

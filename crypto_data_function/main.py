import logging
import os
from typing import List

import alpaca_trade_api as tradeapi
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


def historical_data(symbols: List[str] = ['BTCUSD'], start_timestamp: str = '2009-01-01T00:00:00-00:00'):
    gcs_storage = CloudStorageUtils()

    aps = tradeapi.REST(key_id=API_KEY,
                        secret_key=SECRET_KEY,
                        base_url='https://paper-api.alpaca.markets')

    for symbol in symbols:

        logger.warning(f"Saving historical data for {symbol}")
        history = aps.get_crypto_bars([symbol], TimeFrame.Minute, start=start_timestamp).df

        latest_bar_data = history.index.format()[0].replace(" ", "_")

        history.to_parquet(path=f'/tmp/{latest_bar_data}_{symbol}.pq', compression='snappy')

        gcs_storage.save_data_to_cloud_storage(bucket_name='crypto_data_collection',
                                               file_name=f'{symbol}/{latest_bar_data}_{symbol}.pq',
                                               parquet_file=f'/tmp/{latest_bar_data}_{symbol}.pq')


@app.route("/", methods=['POST'])
def handler():
    data = request.get_json()
    logger.warning(f"The data is : {data}")
    symbols = data.get('SYMBOLS')
    start_timestamp = data.get('START_DATE')

    for symbol in symbols:
        if data.get('SCRAPING_TYPE') == 'history':
            historical_data(symbols=symbol, start_timestamp=start_timestamp)
        else:
            main(symbol=symbol)

    return "OK"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

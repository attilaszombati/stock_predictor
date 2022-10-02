import logging
import os
from datetime import datetime, timedelta

import alpaca_trade_api as tradeapi
import pandas as pd
from alpaca.data import TimeFrame
from alpaca_trade_api import REST
from flask import Flask, request

from utils.cloud_storage import CloudStorageUtils

logger = logging.getLogger('twitter-scraper')

app = Flask(__name__)

API_KEY = 'AKRKQK0FZP17RH0TS516'
SECRET_KEY = 'GszzkYig0nXUMquNyz0Viw1R95oiSKi0KjJOcz4C'


def fingerprint_is_up_to_date(fingerprint: str = None) -> bool:
    now_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S-00:00")

    return now_timestamp < fingerprint


def main(api, symbol: str = 'BTCUSD'):
    gcs_storage = CloudStorageUtils()

    fingerprint = gcs_storage.get_fingerprint_for_user(
        bucket_name='crypto_data_collection',
        file_name=f'{symbol}/fingerprint.csv'
    )

    if not fingerprint_is_up_to_date(fingerprint=fingerprint):
        historical_data(api=api, symbol=symbol, start_timestamp=fingerprint)

    time_frame = TimeFrame.Minute

    data = api.get_crypto_bars(
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


def historical_data(api, symbol: str = 'BTCUSD', start_timestamp: str = '2009-01-01T00:00:00-00:00'):
    gcs_storage = CloudStorageUtils()

    freq = '3m'

    time_format = "%Y-%m-%dT%H:%M:%S-00:00"
    offset_time = datetime.now() + timedelta(weeks=15)
    end_timestamp = offset_time.strftime(time_format)

    dates = pd.date_range(start=start_timestamp, end=end_timestamp, freq=freq,
                          inclusive='both').strftime(time_format).to_list()
    shift_dates = [[i, j] for i, j in zip(dates, dates[1:])]

    for start, end in shift_dates:
        logger.warning(f"Saving historical data from : {start} to : {end} for {symbol} to cloud storage")
        data = api.get_crypto_bars(
            symbol=symbol,
            timeframe=TimeFrame.Minute,
            start=start,
            end=end
        ).df
        if not data.empty:
            latest_bar_data = data.index.format()[-1].replace(" ", "_")
            data.to_parquet(path=f'/tmp/{latest_bar_data}_{symbol}.pq', compression='snappy')
            logger.warning(f"Saving {latest_bar_data} data for {symbol} to cloud storage")

            gcs_storage.save_data_to_cloud_storage(bucket_name='crypto_data_collection',
                                                   file_name=f'{symbol}/{latest_bar_data}_{symbol}.pq',
                                                   parquet_file=f'/tmp/{latest_bar_data}_{symbol}.pq')

    fingerprint = data.index.format()[-1]

    logger.warning(f"Setting fingerprint for {symbol} to {fingerprint}")

    gcs_storage.set_fingerprint_for_user(
        bucket_name='crypto_data_collection',
        file_name=f'{symbol}/fingerprint.csv',
        fingerprint=fingerprint
    )


@app.route("/", methods=['POST'])
def handler():
    data = request.get_json()
    logger.warning(f"The data is : {data}")
    symbols = data.get('SYMBOLS')
    start_timestamp = data.get('START_DATE')

    api = tradeapi.REST(key_id=API_KEY,
                        secret_key=SECRET_KEY,
                        base_url='https://paper-api.alpaca.markets')

    for symbol in symbols:
        if data.get('SCRAPING_TYPE') == 'history':
            historical_data(api=api, symbol=symbol, start_timestamp=start_timestamp)
        else:
            main(api=api, symbol=symbol)

    return "OK"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

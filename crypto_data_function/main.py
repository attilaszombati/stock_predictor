import logging
import os
from datetime import datetime, timedelta

import alpaca_trade_api as tradeapi
import pandas as pd
from alpaca.data import TimeFrame
from flask import Flask, request

from utils.secret_manager import SecretManger
from utils.cloud_storage import CloudStorageUtils

logger = logging.getLogger('twitter-scraper')

app = Flask(__name__)

secret_manager = SecretManger()

API_KEY = secret_manager.get_secret(secret_name='projects/48536241023/secrets/alpaca-api/versions/2')
SECRET_KEY = secret_manager.get_secret(secret_name='projects/48536241023/secrets/alpaca-secret-key/versions/2')


def fingerprint_is_up_to_date(fingerprint: str = None) -> bool:
    now_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S-00:00')

    return now_timestamp < fingerprint


def main(api, symbol: str = 'BTCUSD'):
    gcs_storage = CloudStorageUtils()

    fingerprint = gcs_storage.get_fingerprint_for_user(
        bucket_name='crypto_data_collection',
        file_name=f'{symbol}/fingerprint.csv'
    )

    logger.warning(f'Current fingerprint for {symbol} is {fingerprint}')

    if not fingerprint_is_up_to_date(fingerprint=fingerprint):
        logger.warning(f'Fingerprint is not up to date for {symbol}')
        historical_data(api=api, symbol=symbol, start_timestamp=fingerprint, update_history=True)

    time_frame = TimeFrame.Minute

    data = api.get_crypto_bars(
        symbol=symbol,
        timeframe=time_frame.value
    ).df.iloc[[-1]]
    latest_bar_data = data.index.format()[0].replace(' ', '_')
    data.to_parquet(path=f'/tmp/{latest_bar_data}_{symbol}.pq', compression='snappy')
    logger.warning(f'Saving {latest_bar_data} data for {symbol} to cloud storage')

    gcs_storage.save_data_to_cloud_storage(bucket_name='crypto_data_collection',
                                           file_name=f'{symbol}/{latest_bar_data}_{symbol}.pq',
                                           parquet_file=f'/tmp/{latest_bar_data}_{symbol}.pq')

    updated_fingerprint = data.index.format()[-1]

    logger.warning(f'Setting fingerprint for {symbol} to {updated_fingerprint}')

    gcs_storage.set_fingerprint_for_user(
        bucket_name='crypto_data_collection',
        file_name=f'{symbol}/fingerprint.csv',
        fingerprint=updated_fingerprint
    )

    return updated_fingerprint


def historical_data(api, symbol: str = 'BTCUSD', start_timestamp: str = '2009-01-01T00:00:00-00:00',
                    update_history=False):
    gcs_storage = CloudStorageUtils()
    time_format = '%Y-%m-%dT%H:%M:%S-00:00'
    freq = '3m'

    if update_history:
        offset_time = datetime.now() + timedelta(days=1)
        end_timestamp = offset_time.strftime(time_format)
        range_config = {
            'start': start_timestamp,
            'end': end_timestamp,
            'inclusive': 'both'
        }
    else:
        offset_time = datetime.now() + timedelta(weeks=15)
        end_timestamp = offset_time.strftime(time_format)
        range_config = {
            'start': start_timestamp,
            'end': end_timestamp,
            'freq': freq,
            'inclusive': 'both'
        }

    dates = pd.date_range(**range_config).strftime(time_format).to_list()
    shift_dates = [[i, j] for i, j in zip(dates, dates[1:])]

    for start, end in shift_dates:
        logger.warning(f'Saving historical data from : {start} to : {end} for {symbol} to cloud storage')
        data = api.get_crypto_bars(
            symbol=symbol,
            timeframe=TimeFrame.Minute,
            start=start,
            end=end
        ).df
        if not data.empty:
            latest_bar_data = data.index.format()[-1].replace(' ', '_')
            data.to_parquet(path=f'/tmp/{latest_bar_data}_{symbol}.pq', compression='snappy')
            logger.warning(f'Saving {latest_bar_data} data for {symbol} to cloud storage')

            gcs_storage.save_data_to_cloud_storage(bucket_name='crypto_data_collection',
                                                   file_name=f'{symbol}/{latest_bar_data}_{symbol}.pq',
                                                   parquet_file=f'/tmp/{latest_bar_data}_{symbol}.pq')

    fingerprint = data.index.format()[-1]

    logger.warning(f'Setting fingerprint for {symbol} to {fingerprint}')

    gcs_storage.set_fingerprint_for_user(
        bucket_name='crypto_data_collection',
        file_name=f'{symbol}/fingerprint.csv',
        fingerprint=fingerprint
    )


@app.route('/', methods=['POST'])
def handler():
    data = request.get_json()
    logger.warning(f'The data is : {data}')
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

    return 'OK'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

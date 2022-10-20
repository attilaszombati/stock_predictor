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


def fingerprint_is_up_to_date(fingerprint: str = None, symbol_type: str = 'crypto') -> bool:
    if symbol_type == 'crypto':
        now_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S-00:00')
    else:
        now_timestamp = (datetime.now() - timedelta(hours=2, minutes=15)).strftime('%Y-%m-%d %H:%M:%S-00:00')

    return now_timestamp < fingerprint


def convert_columns_to_float64(df, columns):
    for column in columns:
        df[column] = df[column].astype('float64')
    df.reset_index(inplace=True)
    df["timestamp"] = df["timestamp"].astype(int) // 10 ** 9

    return df


class AlpacaDataFunction:

    def __init__(self, symbol: str = '', update_history: bool = False):
        self.symbol = symbol
        self.update_history = update_history
        self.api = tradeapi.REST(
            base_url='https://paper-api.alpaca.markets',
            key_id=API_KEY,
            secret_key=SECRET_KEY,
            api_version='v2'
        )

    def get_latest_data(self, start_timestamp: str = None, end_timestamp: str = None, time_frame=TimeFrame.Minute):
        raise NotImplementedError('This method must be implemented in a subclass')

    def get_first_data_time(self, data: pd.DataFrame):
        fingerprint = data.index.format()[-1]
        earliest_bar_data = data.index.format()[0]
        first_bar_data = earliest_bar_data.replace(' ', '_')
        return fingerprint, first_bar_data

    def get_historical_data(self, symbol: str, bucket_name: str, symbol_type: str, start_timestamp: str = None,
                            end_timestamp: str = None):
        raise NotImplementedError('This method must be implemented in a subclass')

    def create_historical_data_range(self, start_timestamp: str, end_timestamp: str):
        raise NotImplementedError('This method must be implemented in a subclass')

    def create_latest_data_range(self, start_timestamp: str, end_timestamp: str):
        raise NotImplementedError('This method must be implemented in a subclass')

    def check_data_empty(self, data: pd.DataFrame):
        raise NotImplementedError('This method must be implemented in a subclass')

    @staticmethod
    def convert_columns_to_float64(data: pd.DataFrame, columns):
        for column in columns:
            data[column] = data[column].astype('float64')
        data.reset_index(inplace=True)
        data["timestamp"] = data["timestamp"].astype(int) // 10 ** 9

        return data

    def convert_data_to_parquet(self, data: pd.DataFrame, latest_bar_data: str):
        data.to_parquet(path=f'/tmp/{latest_bar_data}_{self.symbol}.pq', compression='snappy')
        logger.warning(f'Saving {latest_bar_data} data for {self.symbol} to cloud storage')


class AlpacaCryptoDataFunction(AlpacaDataFunction):

    def __int__(self, symbol: str):
        super().__init__(symbol=symbol)
        self.symbol = symbol

    def get_latest_data(self, start_timestamp: str = None, end_timestamp: str = None, time_frame=TimeFrame.Minute):
        data = self.api.get_crypto_bars(
            symbol=self.symbol,
            timeframe=time_frame.value
        ).df.iloc[[-1]]

        return data

    def get_historical_data(self, symbol: str, bucket_name: str, symbol_type: str, start_timestamp: str = None,
                            end_timestamp: str = None):
        pass

    def create_historical_data_range(self, start_timestamp: str, end_timestamp: str):
        pass

    def create_latest_data_range(self, start_timestamp: str, end_timestamp: str, time_frame=TimeFrame.Minute):
        pass

    def check_data_empty(self, data: pd.DataFrame):
        pass


class AlpacaStockDataFunction(AlpacaDataFunction):

    def __int__(self, symbol: str):
        super().__init__(symbol=symbol)
        self.symbol = symbol

    def get_latest_data(self, start_timestamp: str = None, end_timestamp: str = None, time_frame=TimeFrame.Minute):
        data = self.api.get_bars(
            symbol=self.symbol,
            timeframe=time_frame.value
        ).df.iloc[[-1]]

        return data

    def get_historical_data(self, symbol: str, bucket_name: str, symbol_type: str, start_timestamp: str = None,
                            end_timestamp: str = None):
        raise NotImplementedError('This method must be implemented in a subclass')

    def create_historical_data_range(self, start_timestamp: str, end_timestamp: str):
        raise NotImplementedError('This method must be implemented in a subclass')

    def create_latest_data_range(self, start_timestamp: str, end_timestamp: str, time_frame=TimeFrame.Minute):
        pass

    def check_data_empty(self, data: pd.DataFrame):
        raise NotImplementedError('This method must be implemented in a subclass')


def main(api, symbol: str = 'BTCUSD', bucket_name='crypto_data_collection', symbol_type='crypto'):
    gcs_storage = CloudStorageUtils()

    fingerprint = gcs_storage.get_fingerprint_for_user(
        bucket_name=bucket_name,
        file_name=f'{symbol}/fingerprint.csv'
    )

    logger.warning(f'Current fingerprint for {symbol} is {fingerprint}')
    logger.warning(f'The symbol type is {symbol_type}')

    if not fingerprint_is_up_to_date(fingerprint=fingerprint, symbol_type=symbol_type):
        logger.warning(f'Fingerprint is not up to date for {symbol}, historical data will be updated')
        historical_data(api=api, symbol=symbol, start_timestamp=fingerprint, update_history=True,
                        symbol_type=symbol_type, bucket_name=bucket_name)

    if symbol_type == 'crypto':
        alpaca = AlpacaCryptoDataFunction(symbol=symbol)
    else:
        alpaca = AlpacaStockDataFunction(symbol=symbol)

    data = alpaca.get_latest_data()

    fingerprint, first_bar_data = alpaca.get_first_data_time(data=data)
    converted_data = alpaca.convert_columns_to_float64(data=data, columns=['open', 'high', 'low', 'close', 'volume'])

    alpaca.convert_data_to_parquet(data=converted_data, latest_bar_data=first_bar_data)

    logger.warning(f'Saving {first_bar_data} data for {symbol} to cloud storage')

    gcs_storage.save_data_to_cloud_storage(bucket_name=bucket_name,
                                           file_name=f'{symbol}/{first_bar_data}_{symbol}.pq',
                                           parquet_file=f'/tmp/{first_bar_data}_{symbol}.pq')

    logger.warning(f'Setting fingerprint for {symbol} to {first_bar_data}')

    gcs_storage.set_fingerprint_for_user(
        bucket_name=bucket_name,
        file_name=f'{symbol}/fingerprint.csv',
        fingerprint=fingerprint
    )

    return fingerprint


def historical_data(
        api,
        symbol: str = 'BTCUSD',
        start_timestamp: str = '2009-01-01T00:00:00-00:00',
        update_history=False,
        bucket_name='crypto_data_collection',
        symbol_type='crypto'
):
    gcs_storage = CloudStorageUtils()
    time_format = '%Y-%m-%dT%H:%M:%S-00:00'
    freq = '3m'

    if update_history:
        if symbol_type == 'crypto':
            offset_time = datetime.now() + timedelta(days=1)
        else:
            offset_time = datetime.now() - timedelta(hours=2, minutes=15)
        end_timestamp = offset_time.strftime(time_format)
        range_config = {
            'start': start_timestamp,
            'end': end_timestamp,
            'inclusive': 'both'
        }
    else:
        if symbol_type == 'crypto':
            offset_time = datetime.now() + timedelta(weeks=15)
        else:
            offset_time = datetime.now() - timedelta(hours=2, minutes=15)
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

        if symbol_type == 'crypto':
            data = api.get_crypto_bars(
                symbol=symbol,
                timeframe=TimeFrame.Minute,
                start=start,
                end=end
            ).df
        else:
            data = api.get_bars(
                symbol=symbol,
                timeframe=TimeFrame.Minute,
                start=start,
                end=end
            ).df

        if not data.empty:
            logger.warning(f'Saving historical data from : {start} to : {end} for {symbol} to cloud storage')
            index_timestamp_raw = data.index.format()[0]
            latest_bar_data = index_timestamp_raw.replace(' ', '_')
            converted_data = convert_columns_to_float64(df=data, columns=['open', 'high', 'low', 'close', 'volume'])
            converted_data.to_parquet(path=f'/tmp/{latest_bar_data}_{symbol}.pq', compression='snappy')
            logger.warning(f'Saving {latest_bar_data} data for {symbol} to cloud storage')

            gcs_storage.save_data_to_cloud_storage(bucket_name=bucket_name,
                                                   file_name=f'{symbol}/{latest_bar_data}_{symbol}.pq',
                                                   parquet_file=f'/tmp/{latest_bar_data}_{symbol}.pq')

        else:
            logger.warning(f'No data for {symbol} between {start} and {end}')

    fingerprint = index_timestamp_raw

    logger.warning(f'Setting fingerprint for {symbol} to {fingerprint}')

    gcs_storage.set_fingerprint_for_user(
        bucket_name=bucket_name,
        file_name=f'{symbol}/fingerprint.csv',
        fingerprint=fingerprint
    )


@app.route('/', methods=['POST'])
def handler():
    data = request.get_json()
    logger.warning(f'The data is : {data}')
    symbols = data.get('SYMBOLS', 'BTCUSD')
    start_timestamp = data.get('START_DATE', '2009-01-01T00:00:00-00:00')
    bucket_name = data.get('BUCKET_NAME', 'crypto_data_collection')
    symbol_type = data.get('SYMBOL_TYPE', 'crypto')

    api = tradeapi.REST(key_id=API_KEY,
                        secret_key=SECRET_KEY,
                        base_url='https://paper-api.alpaca.markets')

    for symbol in symbols:
        if data.get('SCRAPING_TYPE') == 'history':
            historical_data(
                api=api,
                symbol=symbol,
                start_timestamp=start_timestamp,
                bucket_name=bucket_name,
                symbol_type=symbol_type
            )
        else:
            main(api=api, symbol=symbol, bucket_name=bucket_name, symbol_type=symbol_type)
    return 'OK'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

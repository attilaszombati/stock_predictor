import os
import time

from alpaca.data import CryptoHistoricalDataClient, CryptoBarsRequest, TimeFrame, TimeFrameUnit
from alpaca_trade_api import REST
from flask import Flask
from utils.cloud_storage import CloudStorageUtils

app = Flask(__name__)

API_KEY = 'AKRKQK0FZP17RH0TS516'
SECRET_KEY = 'GszzkYig0nXUMquNyz0Viw1R95oiSKi0KjJOcz4C'


def history():
    print("Hello main function")
    # Instantiate REST API Connection
    api = CryptoHistoricalDataClient(api_key=API_KEY, secret_key=SECRET_KEY)
    request_obj = CryptoBarsRequest(symbol_or_symbols='ETH/USD',
                                    timeframe=TimeFrame(amount=1, unit=TimeFrameUnit.Minute),
                                    start='2018-01-01 00:00:00',
                                    end='2022-08-01 00:00:00')

    history_btc_usd = api.get_crypto_bars(request_params=request_obj).df
    print(history_btc_usd)


@app.route("/", methods=['POST'])
def handler():
    api = REST(key_id=API_KEY, secret_key=SECRET_KEY, base_url="https://paper-api.alpaca.markets")
    bars = api.get_crypto_bars("BTCUSD", TimeFrame.Minute).df.iloc[[-1]]
    timestamp = time.time()
    bars.to_parquet(path=f'/tmp/BTCUSD_{timestamp}.pq', compression='snappy')
    print("Saving to cloud storage")
    storage = CloudStorageUtils()
    storage.save_data_to_cloud_storage(bucket_name='crypto_data_collection',
                                       file_name=f'BTCUSD/{timestamp}.pq',
                                       parquet_file=f'/tmp/BTCUSD_{timestamp}.pq')
    return bars.to_json()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

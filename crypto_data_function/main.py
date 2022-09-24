import time
import os

from flask import Flask, request
from alpaca_trade_api import REST, TimeFrame

from utils.cloud_storage import CloudStorageUtils

app = Flask(__name__)

API_KEY = 'AK2356RHR3VZ4KDCHYQB'
SECRET_KEY = 'kjHUQS6RZHHiwneTl9MvZ7VAcLUictIncBLjsjx0'


def main():
    print("Hello main function")
    # Instantiate REST API Connection
    api = REST(key_id=API_KEY, secret_key=SECRET_KEY, base_url="https://paper-api.alpaca.markets")

    while True:
        # Fetch 1Minute historical bars of Bitcoin
        bars = api.get_crypto_bars("BTCUSD", TimeFrame.Minute).df
        print(bars.iloc[[-1]].to_json())
        time.sleep(60)


@app.route("/", methods=['POST'])
def handler():
    api = REST(key_id=API_KEY, secret_key=SECRET_KEY, base_url="https://paper-api.alpaca.markets")
    bars = api.get_crypto_bars("BTCUSD", TimeFrame.Minute).df
    timestamp = time.time()
    bars.to_parquet(path=f'/tmp/BTCUSD_{timestamp}.pq', compression='snappy')
    storage = CloudStorageUtils()
    storage.save_data_to_cloud_storage(bucket_name='crypto_data_collection',
                                       file_name=f'BTCUSD/{timestamp}.pq',
                                       parquet_file=f'/tmp/BTCUSD_{timestamp}.pq')
    return {"asd": "ok"}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

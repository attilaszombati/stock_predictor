import time

from alpaca_trade_api import REST, TimeFrame

API_KEY = 'AK2356RHR3VZ4KDCHYQB'
SECRET_KEY = 'kjHUQS6RZHHiwneTl9MvZ7VAcLUictIncBLjsjx0'

# Instantiate REST API Connection
api = REST(key_id=API_KEY, secret_key=SECRET_KEY, base_url="https://paper-api.alpaca.markets")

if __name__ == "__main__":
    while True:
        # Fetch 1Minute historical bars of Bitcoin
        bars = api.get_crypto_bars("BTCUSD", TimeFrame.Minute).df

        print("X" * 50)
        print(bars.iloc[[-1]])
        print("X" * 50)
        time.sleep(60)

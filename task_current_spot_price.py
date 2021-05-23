from binance_service import binance_client

import time

import app
from model_service import sync_spot_prices

def task_current_spot_price():
    time.sleep(5)

    while app.running:
        try:
            spot_prices = binance_client.get_orderbook_tickers()
            sync_spot_prices(spot_prices)
        except Exception as ex:
            pass

        time.sleep(0.05)
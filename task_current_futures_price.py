from binance_service import binance_client
import time

import app
from model_service import sync_futures_prices

def task_current_futures_price():
    time.sleep(5)

    while app.running:
        futures_prices = binance_client.futures_coin_mark_price()
        sync_futures_prices(futures_prices)

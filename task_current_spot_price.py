from binance_service import binance_client
import time

import app
from model_service import sync_spot_prices

def task_current_spot_price():
    time.sleep(5)

    while app.running:
        spot_prices = binance_client.get_all_tickers()
        sync_spot_prices(spot_prices)

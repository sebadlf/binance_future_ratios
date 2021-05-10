from binance_service import binance_client
import time

import app
from model_service import sync_spot

def task_current_spot():
    while app.running:
        spot = binance_client.get_exchange_info()
        sync_spot(spot['symbols'])

        time.sleep(60)

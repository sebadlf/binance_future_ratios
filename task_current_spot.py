from binance_service import binance_client
import time

import app
from model_service import sync_spot

def task_current_spot():
    while app.running:
        try:
            spot = binance_client.get_exchange_info()
            sync_spot(spot['symbols'])
        except Exception as ex:
            pass

        time.sleep(60)

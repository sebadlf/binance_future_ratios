from binance_service import binance_client
import time
import app
from model_service import sync_futures

def task_current_futures():
    while app.running:
        try:
            futures = binance_client.futures_coin_exchange_info()
            sync_futures(futures['symbols'])
        except Exception as ex:
            pass

        time.sleep(60)

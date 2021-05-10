from binance_service import binance_client
import time
import app
from model_service import sync_futures

def task_current_futures():
    while app.running:
        futures = binance_client.futures_coin_exchange_info()
        sync_futures(futures['symbols'])

        time.sleep(60)

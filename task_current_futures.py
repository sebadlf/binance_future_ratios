from binance_service import binance_client
import time
import app
import model
from model_service import sync_futures

engine = model.get_engine()

def task_current_futures():
    engine.dispose()

    while app.running:
        try:
            futures = binance_client.futures_coin_exchange_info()
            sync_futures(engine, futures['symbols'])
        except Exception as ex:
            pass

        time.sleep(60)


if __name__ == '__main__':
    task_current_futures()
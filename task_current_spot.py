from binance_service import binance_client
import time

import app
from model_service import sync_spot

import model

engine = model.get_engine()

def task_current_spot():
    engine.dispose()

    while app.running:
        try:
            spot = binance_client.get_exchange_info()
            sync_spot(engine, spot['symbols'])
        except Exception as ex:
            print(ex)
            pass

        time.sleep(60)

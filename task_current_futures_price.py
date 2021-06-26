from streams import ThreadedWebsocketManager, FuturesType
from binance_service import binance_client

import traceback

import keys

import time

import app
from model_service import sync_futures_prices, get_current_futures

import model

cache = dict()

engine = model.get_engine()

def task_current_futures_price():
    engine.dispose()

    time.sleep(5)

    twm = ThreadedWebsocketManager(api_key=keys.api_key, api_secret=keys.api_secret)
    twm.start()

    def handle_socket_message(msg):
        data = msg['data']

        symbol = data['s']
        # print(symbol)

        cache[symbol] = data

    streams = [f"{symbol.lower()}@bookTicker" for symbol in get_current_futures(process_engine=engine)]

    twm.start_futures_multiplex_socket(callback=handle_socket_message, streams=streams, futures_type=FuturesType.COIN_M)

    while app.running:
        try:
            to_save = []

            while len(cache):
                item_key, item_value = cache.popitem()
                to_save.append(item_value)

            if len(to_save):
                sync_futures_prices(engine, to_save)
        except Exception as ex:
            print(ex)
            traceback.print_stack()

if __name__ == '__main__':
    task_current_futures_price()
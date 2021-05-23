from binance.streams import ThreadedWebsocketManager, FuturesType
from binance_service import binance_client

import traceback

import keys

import time

import app
from model_service import sync_spot_prices, spot_symbols_with_futures

cache = dict()

def task_current_spot_price():
    time.sleep(5)

    twm = ThreadedWebsocketManager(api_key=keys.api_key, api_secret=keys.api_secret)
    twm.start()

    def handle_socket_message(msg):
        data = msg['data']

        symbol = data['s']

        cache[symbol] = data

    streams = [f"{symbol.lower()}@bookTicker" for symbol in spot_symbols_with_futures]

    twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)

    while app.running:
        try:
            to_save = []

            while len(cache):
                item_key, item_value = cache.popitem()
                to_save.append(item_value)

            if len(to_save):
                sync_spot_prices(to_save)
        except Exception as ex:
            print(ex)
            traceback.print_stack()

if __name__ == '__main__':
    task_current_spot_price()
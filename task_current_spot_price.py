from binance.streams import ThreadedWebsocketManager, FuturesType
from binance_service import binance_client

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
        symbol = msg['s']
        if symbol in spot_symbols_with_futures:
            cache[symbol] = msg

    twm.start_book_ticker_socket(callback=handle_socket_message)

    while app.running:
        try:
            to_save = []

            while len(cache):
                key, msg = cache.popitem()
                to_save.append(msg)

            if len(to_save):
                sync_spot_prices(to_save)
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    task_current_spot_price()
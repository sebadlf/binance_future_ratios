from binance_service import binance_client
from binance.streams import ThreadedWebsocketManager
import keys
import app
from model_service import spot_symbols_with_futures

import time

from datetime import datetime

def task_current_spot_price():

    start = None

    twm = ThreadedWebsocketManager(api_key=keys.api_key, api_secret=keys.api_secret)
    twm.start()

    def handle_socket_message(msg):
        # print(datetime.utcnow() - start)
        print(msg)

    # Futures
    # twm.start_coin_futures_socket(handle_socket_message)

    # SPOT
    # twm.start_user_socket(handle_socket_message)


    # streams = [f"{symbol.lower()}@bookTicker" for symbol in spot_symbols_with_futures]

    # twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)

    # twm.start_aggtrade_socket(handle_socket_message, "BNBUSDT")


    # twm.start_user_socket(handle_socket_message)

    # print("running")

    # time.sleep(5)

    # start = datetime.utcnow()

    # binance_client.order_market_sell(symbol="BNBUSDT", quantity=0.0260)

    # [print(x) for x in binance_client.futures_coin_position_information() if]

    # print("done")

    # while app.running:
    #     pass

if __name__ == '__main__':
    task_current_spot_price()
from binance.client import Client
from operator import itemgetter
from keys import api_key, api_secret

import traceback

import model_service

binance_client = Client(api_key, api_secret)

def filter_future_list(futures):
    filtered_futures = filter(lambda x: x['symbol'].find("_PERP") == -1, futures['symbols'])

    sorted_futures = sorted(filtered_futures, key=itemgetter("symbol"))

    return sorted_futures

def get_price_element(prices, symbol):

    price = list(filter(lambda x: x['symbol'] == symbol, prices))[0]

    return price

def get_spot_order(symbol, order_id):
    order = None

    while not order:
        try:
            order = binance_client.get_order(symbol=symbol, orderId=order_id)
        except Exception as e:
            print(e)
            traceback.print_exc()

    return order

def get_future_order(symbol, order_id):
    order = None

    while not order:
        try:
            order = binance_client.futures_coin_get_order(symbol=symbol, orderId=order_id)
        except Exception as e:
            print(e)
            traceback.print_exc()

    return order

def get_spot_trade(symbol, order_id, qty):
    trade = None

    while not trade or (abs((sum([float(t['qty']) for t in trade]) / qty) - 1) > 0.001):
        # binance_trades = binance_client.get_my_trades(symbol=symbol, fromId=from_id)
        binance_trades = binance_client.get_my_trades(symbol=symbol)

        trades = [trade for trade in binance_trades if trade['orderId'] == order_id]

        trade = trades if len(trades) else None

    return trade

def get_future_trade(symbol, order_id, qty):
    trade = None

    while not trade or sum([int(t['qty']) for t in trade]) < qty:
        # binance_trades = binance_client.get_my_trades(symbol=symbol, fromId=from_id)
        binance_trades = binance_client.futures_coin_account_trades(symbol=symbol)

        trades = [trade for trade in binance_trades if trade['orderId'] == int(order_id)]

        trade = trades if len(trades) else None

    return trade

def init_leverages():
    for symbol in model_service.get_current_futures():
        binance_client.futures_coin_change_leverage(symbol=symbol, leverage=1)

if __name__ == '__main__':
    from datetime import datetime

    start = datetime.utcnow()

    print(binance_client.get_order_book(symbol="DOTUSDT", limit=5))
    print(binance_client.get_orderbook_tickers())

    print(datetime.utcnow() - start)
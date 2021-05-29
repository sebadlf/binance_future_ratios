from binance.streams import ThreadedWebsocketManager

import traceback

import keys

import time

import app
from model_service import sync_spot_prices_calc, spot_symbols_with_futures

import model

import config

cache = dict()

engine = model.get_engine()

def price_risk_safe(symbol, book, risk = config.RISK, safe = config.SAFE):
    sum_total_risk, sum_total_safe, sum_size_risk, sum_size_safe = 0, 0, 0, 0
    sum_provisorio_total, sum_provisorio_size = 0, 0
    price_risk, price_safe = 0, 0

    # print(book)

    for i in book:

        size = float(i[1])
        price = float(i[0])

        sum_provisorio_total += price * size
        sum_provisorio_size += size

        if sum_total_risk == 0 and sum_provisorio_total > risk:
            sum_total_risk = sum_provisorio_total
            sum_size_risk = sum_provisorio_size

        elif sum_provisorio_total > safe:
            sum_total_safe = sum_provisorio_total
            sum_size_safe = sum_provisorio_size
            break

    # verificacion para ver si esta bien solo 10 puntas
    if sum_provisorio_total != 0:
        sum_total_safe = sum_provisorio_total
        sum_size_safe = sum_provisorio_size

    # if sum_total_safe < safe:
    #     print(f'no llegó al safe {symbol}')
    #     print(sum_provisorio_total)
        # print(book)


    if sum_size_risk != 0:
        price_risk = sum_total_risk / sum_size_risk
    if sum_total_safe != 0:
        price_safe = sum_total_safe / sum_size_safe

    return price_risk, price_safe


def ppp_order_book(symbol, book, risk = config.RISK, safe = config.SAFE):

    res = {'s' : symbol}

    ask = book['asks']
    bid = book['bids']

    res['ask_risk'], res['ask_safe'] = price_risk_safe(symbol, ask)
    res['bid_risk'], res['bid_safe'] = price_risk_safe(symbol, bid)

    return res


def task_current_spot_price():
    engine.dispose()

    time.sleep(5)

    twm = ThreadedWebsocketManager(api_key=keys.api_key, api_secret=keys.api_secret)
    twm.start()

    def handle_socket_message(msg):

        data = msg['data']

        symbol = tickers_streams[msg['stream']]

        cache[symbol] = data

    streams = [f"{symbol.lower()}@depth{config.DEPTH}@{config.MS}ms" for symbol in spot_symbols_with_futures]
    tickers_streams = {}

    for symbol in spot_symbols_with_futures:
        string = f'@depth{config.DEPTH}@{config.MS}ms'
        tickers_streams[symbol.lower()+string] = symbol

    twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)


    while app.running:

        try:
            to_save = []



            while len(cache):

                item_key, item_value = cache.popitem()
                ppp = ppp_order_book(symbol = item_key, book = item_value)
                to_save.append(ppp)

            if len(to_save):
                sync_spot_prices_calc(engine, to_save)

        except Exception as ex:
            print(ex)
            traceback.print_stack()

if __name__ == '__main__':
    # model.create_tables()

    task_current_spot_price()


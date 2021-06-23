from threading import Thread
from multiprocessing import Process

import time

import model

import model_view

import model_service

from binance_service import binance_client, get_spot_trade, get_spot_order, filter_future_list, get_price_element

import position_service
import binance_service

from task_current_spot import task_current_spot
from task_current_spot_price import task_current_spot_price
from task_current_futures import task_current_futures
from task_current_futures_price import task_current_futures_price
from task_historical_spot import task_historical_spot
from task_historical_ratios_quick import task_historical_ratios_quick
from task_historical_futures import task_historical_futures
from task_current_signal import task_current_signal
from task_stock_bnb import task_stock_bnb, amount_ticker
from task_avg_ratio import task_avg_ratio
from task_spot_order_book import task_current_spot_order_book
from task_futures_order_book import task_current_futures_order_book
from task_account_update import task_account_update
from task_operation_spot_buy import task_operation_spot_buy
from task_operation_transfer import task_operation_transfer
from task_operation_future_sell import task_operation_future_sell
from task_operation_future_buy import task_operation_future_buy
from task_operation_spot_sell import task_operation_spot_sell
from task_max_ratio_avg import task_max_historical_ratio

import utils


def init_leverages():
    for symbol in model_service.get_current_futures():
        binance_client.futures_coin_change_leverage(symbol=symbol, leverage=1)
        try:
            binance_client.futures_coin_change_margin_type(symbol=symbol, marginType="ISOLATED")
        except:
            pass

if __name__ == '__main__':
    model.create_tables()

    model_view.create_views()

    init_leverages()

    task_current_futures = Thread(name="task_current_futures", target=task_current_futures)
    task_current_futures.start()

    task_current_spot = Thread(name="task_current_spot", target=task_current_spot)
    task_current_spot.start()

    task_current_spot_price = Process(name="task_current_spot_price", target=task_current_spot_price)
    task_current_spot_price.start()

    task_current_futures_price = Process(name="task_current_futures_price", target=task_current_futures_price)
    task_current_futures_price.start()

    task_historical_ratios_quick = Process(name="task_historical_ratios_quick", target=task_historical_ratios_quick)
    task_historical_ratios_quick.start()

    task_historical_spot = Thread(name="task_historical_spot", target=task_historical_spot)
    task_historical_spot.start()

    task_historical_futures = Thread(name="task_historical_futures", target=task_historical_futures)
    task_historical_futures.start()

    tickers = utils.currencies()
    tickers = tickers[0]

    task_avg_ratio1 = Process(name="task_avg_ratio", target=task_avg_ratio, args=(tickers, 'weekly_avg_year_ratio', 10080))
    task_avg_ratio1.start()

    task_avg_ratio2 = Process(name="task_avg_ratio", target=task_avg_ratio, args=(tickers, 'daily_avg_year_ratio', 1440))
    task_avg_ratio2.start()

    task_avg_ratio3 = Process(name="task_avg_ratio", target=task_avg_ratio, args=(tickers, 'six_hours_avg_year_ratio', 360))
    task_avg_ratio3.start()

    task_avg_ratio4 = Process(name="task_avg_ratio", target=task_avg_ratio, args=(tickers, 'hourly_avg_year_ratio', 60))
    task_avg_ratio4.start()

    task_avg_ratio5 = Process(name="task_avg_ratio", target=task_avg_ratio, args=(tickers, 'ten_minutes_avg_year_ratio', 10))
    task_avg_ratio5.start()

    task_current_signal = Thread(name="task_current_signal", target=task_current_signal)
    task_current_signal.start()

    task_stock_bnb = Thread(name="task_stock_bnb", target=task_stock_bnb)
    task_stock_bnb.start()

    thread_account_update = Thread(name="task_account_update", target=task_account_update)
    thread_account_update.start()

    thread_operation_transfer = Thread(name="task_operation_transfer", target=task_operation_transfer)
    thread_operation_transfer.start()

    thread_operation_spot_buy = Thread(name="task_operation_spot_buy", target=task_operation_spot_buy)
    thread_operation_spot_buy.start()

    thread_operation_spot_sell = Thread(name="task_operation_spot_sell", target=task_operation_spot_sell)
    thread_operation_spot_sell.start()

    thread_operation_future_buy = Thread(name="task_operation_future_buy", target=task_operation_future_buy)
    thread_operation_future_buy.start()

    thread_operation_future_sell = Thread(name="task_operation_future_sell", target=task_operation_future_sell)
    thread_operation_future_sell.start()

    thread_operation_max_historical_ratio = Thread(name="task_max_historical_ratio", target=task_max_historical_ratio)
    thread_operation_max_historical_ratio.start()




from threading import Thread
from multiprocessing import Process

import time

import model

import model_view

import model_service

from binance_service import binance_client, get_spot_trade, get_spot_order, init_leverages, filter_future_list, get_price_element

import position_service
import binance_service

from task_current_spot import task_current_spot
from task_current_spot_price import task_current_spot_price
from task_current_futures import task_current_futures
from task_current_futures_price import task_current_futures_price
from task_historical_spot import task_historical_spot
from task_historical_futures import task_historical_futures
from task_current_signal import task_current_signal
from task_stock_bnb import task_stock_bnb, amount_ticker
from task_avg_ratio import task_avg_ratio

import utils


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

    task_current_signal = Thread(name="task_current_signal", target=task_current_signal, args=(tickers, ))
    task_current_signal.start()

    task_stock_bnb = Thread(name="task_stock_bnb", target=task_stock_bnb)
    task_stock_bnb.start()

    time.sleep(10)

    print("Start")

    amount_usdt = amount_ticker("USDT")

    while True:

        if amount_usdt > 25:
            positions_to_open = model_service.get_current_ratios()

            if len(positions_to_open):
                best_position = [row for row in model_service.get_current_ratios()][0]

                print("Abro posición", best_position)

                position_data = position_service.open_position(best_position)

                print("position_data", position_data)

                position_service.save_opened_position(position_data)

                amount_usdt = amount_ticker("USDT")

        ###########################

        positions_to_close = model_service.get_current_operations_to_close()

        if len(positions_to_close):
            position_to_close = [row for row in model_service.get_current_operations_to_close()][0]

            direct_ratio_diff = position_to_close['direct_ratio_diff']

            print(f"Cierror posición con diff = {round(direct_ratio_diff, 4)}", position_to_close)

            position_data = position_service.close_position(position_to_close)

            print(position_data)

            position_service.save_closed_position(position_data)

            amount_usdt = amount_ticker("USDT")



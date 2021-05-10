from datetime import datetime, timezone
from threading import Thread

import time

import model_service

from binance_service import binance_client, filter_future_list, get_price_element

from task_current_spot import task_current_spot
from task_current_spot_price import task_current_spot_price
from task_current_futures import task_current_futures
from task_current_futures_price import task_current_futures_price

task_current_futures = Thread(name="task_current_futures", target=task_current_futures)
task_current_futures.start()

task_current_spot = Thread(name="task_current_spot", target=task_current_spot)
task_current_spot.start()

task_current_spot_price = Thread(name="task_current_spot_price", target=task_current_spot_price)
task_current_spot_price.start()

task_current_futures_price = Thread(name="task_current_futures_price", target=task_current_futures_price)
task_current_futures_price.start()



time.sleep(10)

[print(x) for x in model_service.get_current_ratios()]

# futures = filter_future_list(binance_client.futures_coin_exchange_info())
#
# spot_prices = binance_client.get_all_tickers()
#
# future_prices = binance_client.futures_coin_mark_price()
#
# for future in futures:
#     if future['symbol'].startswith("XRP") or future['symbol'].startswith("DOT") or True:
#
#         now = datetime.now(tz=timezone.utc)
#         end_date = datetime.fromtimestamp(future['deliveryDate'] / 1000, tz=timezone.utc)
#
#         time_difference = end_date - now
#
#         hours = round(time_difference.days * 24 + time_difference.seconds / 3600)
#
#         spot_price_data = get_price_element(spot_prices, future['pair'] + "T")
#         future_price_data = get_price_element(future_prices, future['symbol'])
#
#         future_symbol = future_price_data['symbol']
#         future_price = float(future_price_data['markPrice'])
#         spot_symbol = spot_price_data['symbol']
#         spot_price = float(spot_price_data['price'])
#
#         ratio = future_price / spot_price - 1
#
#         hour_ratio = ratio / hours
#
#         #print(ratio, hour_ratio)
#
#         year_ratio = hour_ratio * 365 * 24 * 100
#
#         print(round(year_ratio, 2), round(ratio * 100,2), future_symbol, future_price, spot_symbol, spot_price, (spot_price/future_price * 100))
#
#

from datetime import datetime, timezone
from threading import Thread

import time

import model_service


from binance_service import binance_client, get_spot_trade, get_spot_order, init_leverages, filter_future_list, get_price_element

import position_service

from task_current_spot import task_current_spot
from task_current_spot_price import task_current_spot_price
from task_current_futures import task_current_futures
from task_current_futures_price import task_current_futures_price
from task_historical_spot import task_historical_spot
from task_historical_futures import task_historical_futures
from task_current_signal import task_current_signal

task_current_futures = Thread(name="task_current_futures", target=task_current_futures)
task_current_futures.start()

task_current_spot = Thread(name="task_current_spot", target=task_current_spot)
task_current_spot.start()

task_current_spot_price = Thread(name="task_current_spot_price", target=task_current_spot_price)
task_current_spot_price.start()

task_current_futures_price = Thread(name="task_current_futures_price", target=task_current_futures_price)
task_current_futures_price.start()

task_historical_spot = Thread(name="task_historical_spot", target=task_historical_spot)
task_historical_spot.start()

task_historical_futures = Thread(name="task_historical_futures", target=task_historical_futures)
task_historical_futures.start()

# init_leverages()

time.sleep(10)

task_current_signal = Thread(name="task_current_signal", target=task_current_signal)
task_current_signal.start()

# best_position = [row for row in model_service.get_current_ratios()][0]
#
# position_data = position_service.open_position(best_position)
#
# position_service.save_opened_position(position_data)

print("It Works!")

from binance_service import binance_client
import time
import app
import model

import model_service
import utils

from config import SPOT_BUY_OVERBUY_MARGIN, MIN_NUMBER_OF_CONTRACTS

engine = model.get_engine()

import uuid

import traceback

def task_current_futures():
    engine.dispose()

    while app.running:
        try:
            spot_order = None

            best_position = [row for row in model_service.get_current_ratios()][0]

            print("Abro posición", best_position)

            spot_symbol = best_position['spot_symbol']
            buy_per_contract = best_position['buy_per_contract']
            tick_size = best_position['tick_size']

            quantity_to_buy = buy_per_contract * SPOT_BUY_OVERBUY_MARGIN * MIN_NUMBER_OF_CONTRACTS
            quantity_to_buy = utils.get_quantity_rounded(quantity_to_buy, tick_size)

            spot_order = binance_client.order_market_buy(symbol=spot_symbol, quantity=quantity_to_buy)

            model_service.save_spot_order(best_position, spot_order)

        except Exception as ex:
            print("Error al crear posicion")
            print(best_position, spot_order)
            print(ex)
            traceback.print_stack()

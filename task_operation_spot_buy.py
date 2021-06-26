from binance_service import binance_client
import time
import app
import model

import model_service
import utils

from config import SPOT_BUY_OVERBUY_MARGIN

import traceback
import model_helper
from sqlalchemy.orm import Session

def save_operation_buy_spot(position_dict, spot_order_dict):
    with Session(model.get_engine()) as session:
        with session.begin():
            # spot_order
            order_id = spot_order_dict['orderId']

            spot_order = session.query(model.SpotOrder).filter_by(order_id=order_id).first()
            spot_order = model_helper.sync_spot_order(spot_order_dict, spot_order)

            # operation
            operation = spot_order.operation

            # position
            position = operation.position if operation else None

            if not position:
                position_id = position_dict['position_id']

                if position_id:
                    position = session.query(model.Position).get(position_id)
                else:
                    position = model.Position()
                    session.add(position)

            position = model_helper.sync_position({
                **position_dict,
                'state': 'CREATED'
            }, position)

            if not operation:
                operation = model.Operation()

                position.operations.append(operation)

                operation.spot_order = spot_order

            operation = model_helper.sync_operation({
                **position_dict,
                'kind': 'OPEN',
                'state': 'SPOT_BUY'
            }, operation)

def resetSpotBalance(asset):
    with Session(model.get_engine()) as session, session.begin():
        spot_balance = session.query(model.SpotBalance).get(asset)
        spot_balance.outdated = True

def task_operation_spot_buy():
    while app.running:
        try:
            best_position = None
            spot_order = None

            best_positions = [row for row in model_service.get_current_ratios_to_open()]

            if len(best_positions):
                best_position = best_positions[0]

                spot_symbol = best_position['spot_symbol']
                buy_per_contract = best_position['buy_per_contract']
                tick_size = best_position['tick_size']
                contract_qty = best_position['contract_qty']
                future_balance = best_position['future_balance']

                quantity_to_buy = buy_per_contract * SPOT_BUY_OVERBUY_MARGIN * contract_qty - future_balance
                quantity_to_buy = utils.get_quantity_rounded(quantity_to_buy, tick_size)

                resetSpotBalance("USDT")

                spot_order = binance_client.order_market_buy(symbol=spot_symbol, quantity=quantity_to_buy)

                save_operation_buy_spot(best_position, spot_order)

        except Exception as ex:
            print("Error comprar spot")
            print(best_position, spot_order)
            print(ex)
            traceback.print_stack()


if __name__ == '__main__':
    # task_operation_spot_buy()
    # position = {'position_id': None, 'future_symbol': 'BCHUSD_210924', 'future_price': 588.23, 'spot_symbol': 'BCHUSDT', 'spot_price': 575.36, 'direct_ratio': 2.2368596087410486, 'hours': 2486, 'hour_ratio': 0.0008997826262031572, 'days': 103, 'year_ratio': 7.882095805539657, 'contract_size': 10, 'buy_per_contract': 0.017000153565840316, 'tick_size': 1e-05, 'base_asset': 'BCH', 'signal': 'open', 'contract_qty': 3.0, 'future_balance': 5.319e-05}
    # order = {'symbol': 'BCHUSDT', 'orderId': 1996268268, 'orderListId': -1, 'clientOrderId': 'kbVO3Lhi9mJ7U4b5g0Roju', 'transactTime': 1623512446046, 'price': '0.00000000', 'origQty': '0.05196000', 'executedQty': '0.05196000', 'cummulativeQuoteQty': '30.08743800', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'fills': [{'price': '579.05000000', 'qty': '0.05196000', 'commission': '0.00006616', 'commissionAsset': 'BNB', 'tradeId': 94362645}]}
    #
    # save_operation_buy_spot(position, order)
    #
    print(model_service.get_current_ratios_to_open())
    # resetSpotBalance('USDT')
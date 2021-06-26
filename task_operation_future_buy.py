from binance_service import binance_client
import app
import model
from typing import Dict

import model_service

import traceback
from sqlalchemy.orm import Session

import model_helper

def save_future_buy(operation_dict: Dict, future_order_dict: Dict):
    future_buy_id = None

    with Session(model.get_engine()) as session:
        with session.begin():
            position_id = operation_dict['position_id']

            position = session.query(model.Position).get(position_id)

            position.state = 'CLOSING'
            position.message = ''

            operation = model_helper.sync_operation({
                **operation_dict,
                'kind': 'CLOSE',
                'state': 'FUTURE_BUY'
            })

            position.operations.append(operation)

            order_id = future_order_dict['orderId']

            future_order = session.query(model.FutureOrder).filter_by(order_id=order_id).first()

            if future_order:
                print(f"Encontre future order = {future_order.id}, {future_order.status}")

            future_buy = model_helper.sync_future_order(future_order_dict, future_order)

            operation.future_order = future_buy

            # future_object = session.query(model.Future).get(operation.future)
            # future_object.balance.outdated = True

        future_buy_id = future_buy.id


    return future_buy_id

def resetFutureBalance(future_symbol):
    with Session(model.get_engine()) as session, session.begin():
        future_object = session.query(model.Future).get(future_symbol)
        future_object.balance.outdated = True

def task_operation_future_buy():

    while app.running:
        try:
            operation_dict = dict()
            future_order = dict()

            pending_operations = model_service.get_current_operations_to_close()

            for operation_dict in pending_operations:
                future_symbol = operation_dict['future_symbol']

                resetFutureBalance(future_symbol)

                future_order = binance_client.futures_coin_create_order(
                    symbol=future_symbol,
                    side="BUY",
                    type="MARKET",
                    quantity=operation_dict['contract_qty']
                )

                save_future_buy(operation_dict, future_order)

        except Exception as ex:
            print("Error comprar future")
            print(operation_dict, future_order)
            print(ex)
            traceback.print_stack()

            model_service.save_position_state(
                operation_dict.get('position_id'),
                f"CLOSING_FAIL",
                ex
            )

if __name__ == '__main__':

    # operations = model_service.get_current_operations_to_close()
    #
    # order0 = {'orderId': 417610461, 'symbol': 'DOTUSD_210924', 'pair': 'DOTUSD', 'status': 'NEW',
    #  'clientOrderId': '2YNXgJmUPIZ87qHSIbFCh1', 'price': '0', 'avgPrice': '0.000', 'origQty': '2', 'executedQty': '0',
    #  'cumQty': '0', 'cumBase': '0', 'timeInForce': 'GTC', 'type': 'MARKET', 'reduceOnly': False, 'closePosition': False,
    #  'side': 'BUY', 'positionSide': 'BOTH', 'stopPrice': '0', 'workingType': 'CONTRACT_PRICE', 'priceProtect': False,
    #  'origType': 'MARKET', 'updateTime': 1624320575731}
    #
    # order1 = {'orderId': 227621494, 'symbol': 'LINKUSD_210924', 'pair': 'LINKUSD', 'status': 'NEW', 'clientOrderId': 'tn2mkKUPGTrWX3A7hPdKQf', 'price': '0', 'avgPrice': '0.000', 'origQty': '6', 'executedQty': '0', 'cumQty': '0', 'cumBase': '0', 'timeInForce': 'GTC', 'type': 'MARKET', 'reduceOnly': False, 'closePosition': False, 'side': 'BUY', 'positionSide': 'BOTH', 'stopPrice': '0', 'workingType': 'CONTRACT_PRICE', 'priceProtect': False, 'origType': 'MARKET', 'updateTime': 1624320579546}
    #
    # save_future_buy(operations[0], order0)
    # save_future_buy(operations[1], order1)



    # import binance_service
    #
    # future_order = binance_service.get_future_order('DOTUSD_210924', '417610461')
    #
    # model_service.save_future_order(model.get_engine(), future_order)
    #
    # future_order = binance_service.get_future_order('LINKUSD_210924', '227621494')
    #
    # model_service.save_future_order(model.get_engine(), future_order)

    future_order_dict = {'e': 'ORDER_TRADE_UPDATE', 'T': 1624660050915, 'E': 1624660050920, 'i': 'mYTifWFzFzTiSg', 'o': {'s': 'BTCUSD_210924', 'c': 'cGrUHhHKzNnu430WIpsUXk', 'S': 'BUY', 'o': 'MARKET', 'f': 'GTC', 'q': '2', 'p': '0', 'ap': '32222.7', 'sp': '0', 'x': 'TRADE', 'X': 'FILLED', 'i': 764575533, 'l': '2', 'z': '2', 'L': '32222.7', 'n': '0.00000310', 'N': 'BTC', 'T': 1624660050915, 't': 8905541, 'b': '0', 'a': '0', 'm': False, 'R': False, 'wt': 'CONTRACT_PRICE', 'ot': 'MARKET', 'ps': 'BOTH', 'cp': False, 'ma': 'BTC', 'rp': '0.00038223', 'pP': False, 'si': 0, 'ss': 0}}

    future_order_dict = future_order_dict['o']

    with Session(model.get_engine()) as session:
        with session.begin():

            order_id = future_order_dict['i']

            future_order = session.query(model.FutureOrder).filter_by(order_id=order_id).first()

            if future_order:
                print(f"Encontre future order = {future_order.id}, {future_order.status}")

            future_buy = model_helper.sync_future_order(future_order_dict, future_order)


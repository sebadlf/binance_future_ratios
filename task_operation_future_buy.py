from binance_service import binance_client
import app
import model
from typing import Dict

import model_service

import traceback
from sqlalchemy.orm import Session

import model_helper

def save_future_buy(operation_dict: Dict, future_order: Dict):
    future_buy_id = None

    try:
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

                future_buy = model_helper.sync_future_order(future_order)

                operation.future_order = future_buy

                session.commit()

                operation.future_relation.balance.outdated = True

            future_buy_id = future_buy.id

    except Exception as ex:
        print(f"Error al guardar Venta de futuro = {future_order}")
        print(ex)
        traceback.print_stack()

    return future_buy_id

def task_operation_future_buy():

    while app.running:
        try:
            operation_dict = dict()
            future_order = dict()

            pending_operations = model_service.get_current_operations_to_close()

            for operation_dict in pending_operations:
                future_order = binance_client.futures_coin_create_order(
                    symbol=operation_dict['future_symbol'],
                    side="BUY",
                    type="MARKET",
                    quantity=operation_dict['contract_qty']
                )

                save_future_buy(operation_dict, future_order)

        except Exception as ex:
            print("Error comprar spot")
            print(operation_dict, future_order)
            print(ex)
            traceback.print_stack()

            model_service.sa(
                operation_dict.get('position_id'),
                f"CLOSING_FAIL",
                ex
            )

if __name__ == '__main__':
    task_operation_future_buy()

    # operation = {'position_id': 4, 'future_symbol': 'BCHUSD_210924', 'future_price': 588.61, 'spot_symbol': 'BCHUSDT',
    #  'spot_price': 575.23, 'direct_ratio': 2.3260270391173288, 'hours': 2361, 'hour_ratio': 0.0009851872253779453,
    #  'days': 98, 'year_ratio': 8.6302400943108, 'contract_size': 10, 'buy_per_contract': 0.016989178316482757,
    #  'tick_size': 1e-05, 'base_asset': 'BCH', 'signal': 'open', 'contract_qty': 3,
    #  'direct_ratio_diff': -0.0891674791045114, 'year_ratio_diff': -0.748144280559579,
    #  'better_future_symbol': 'ETHUSD_210924'}
    #
    # order = {'orderId': 194416583, 'symbol': 'BCHUSD_210924', 'pair': 'BCHUSD', 'status': 'NEW', 'clientOrderId': 'XID6NCoK515fjbMoz2wAeF', 'price': '0', 'avgPrice': '0.00', 'origQty': '3', 'executedQty': '0', 'cumQty': '0', 'cumBase': '0', 'timeInForce': 'GTC', 'type': 'MARKET', 'reduceOnly': False, 'closePosition': False, 'side': 'BUY', 'positionSide': 'BOTH', 'stopPrice': '0', 'workingType': 'CONTRACT_PRICE', 'priceProtect': False, 'origType': 'MARKET', 'updateTime': 1623960560940}
    #
    # save_future_buy(operation, order)

    # import binance_service
    #
    # future_order = binance_service.get_future_order('BCHUSD_210924', '194416583')
    #
    # model_service.save_future_order(model.get_engine(), future_order)


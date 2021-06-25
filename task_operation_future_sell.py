from binance_service import binance_client
import app
import model
from typing import Dict

import model_service

import traceback
from sqlalchemy.orm import Session

import model_helper

def save_future_sell(future_order_dict: Dict):
    future_sell_id = None

    try:
        with Session(model.get_engine()) as session:
            with session.begin():
                operation_id = future_order_dict['operation_id']

                operation = session.query(model.Operation).get(operation_id)

                operation.state = 'FUTURE_SELL'

                order_id = future_order_dict['orderId']

                future_order = session.query(model.FutureOrder).filter_by(order_id=order_id).first()

                future_sell = model_helper.sync_future_order(future_order_dict, future_order)

                operation.future_order = future_sell

            future_sell_id = future_sell.id

    except Exception as ex:
        print(f"Error al guardar Venta de futuro = {future_order_dict}")
        print(ex)
        traceback.print_stack()

    return future_sell_id

def task_operation_future_sell():

    while app.running:
        try:
            operation_dict = dict()
            future_order = dict()

            pending_operations = model_service.get_operations_to_sell_futures()

            for operation_dict in pending_operations:
                future_order = binance_client.futures_coin_create_order(
                    symbol=operation_dict['future_symbol'],
                    side="SELL",
                    type="MARKET",
                    quantity=operation_dict['contract_qty']
                )

                save_future_sell({
                    'operation_id': operation_dict['operation_id'],
                    **future_order
                })

        except Exception as ex:
            print("Error comprar spot")
            print(operation_dict, future_order)
            print(ex)
            traceback.print_stack()

            model_service.save_operation_state(
                operation_dict.get('operation_id'),
                f"FUTURE_SELL_FAIL",
                ex
            )

if __name__ == '__main__':
    pass

    #task_future_sell()

    import binance_service

    future_order = binance_service.get_future_order('BTCUSD_210924', '729382408')

    save_future_sell({
        'operation_id': 52,
        **future_order
    })

    future_order = binance_service.get_future_order('BTCUSD_210924', '729383052')

    save_future_sell({
        'operation_id': 53,
        **future_order
    })


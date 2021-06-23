from binance_service import binance_client
import app
import model
from typing import Dict

import model_service

import traceback
from sqlalchemy.orm import Session

import model_helper

def save_spot_sell(spot_order: Dict):
    spot_sell_id = None

    try:
        with Session(model.get_engine()) as session:
            with session.begin():
                operation_id = spot_order['operation_id']

                operation = session.query(model.Operation).get(operation_id)

                operation.state = 'SPOT_SELL'

                operation.position.state = 'CLOSING'

                spot_sell = model_helper.sync_spot_order(spot_order)

                operation.spot_order = spot_sell

            spot_sell_id = spot_sell.id

    except Exception as ex:
        print(f"Error al guardar Venta de spot = {spot_order}")
        print(ex)
        traceback.print_stack()

    return spot_sell_id

def task_operation_spot_sell():

    while app.running:
        try:
            operation_dict = dict()
            spot_order = dict()

            pending_operations = model_service.get_operations_to_sell_spots()

            for operation_dict in pending_operations:
                spot_order = binance_client.create_order(
                    symbol=operation_dict['spot_symbol'],
                    side="SELL",
                    type="MARKET",
                    quantity=operation_dict['qty']
                )

                save_spot_sell({
                    'operation_id': operation_dict['operation_id'],
                    **spot_order
                })

        except Exception as ex:
            print("Error comprar spot")
            print(operation_dict, spot_order)
            print(ex)
            traceback.print_stack()

            model_service.save_operation_state(
                operation_dict.get('operation_id'),
                f"SPOT_SELL_FAIL",
                ex
            )

if __name__ == '__main__':
    task_operation_spot_sell()

    import binance_service

    # spot_order = binance_service.get_spot_order('BCHUSD_210924', '191648084')
    #
    # save_spot_sell({
    #     'operation_id': 1,
    #     **spot_order
    # })



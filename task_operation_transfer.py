from binance_service import binance_client
import app
import model
from typing import Dict

import model_service

import traceback
from sqlalchemy.orm import Session

def save_transfer(transfer: Dict):
    transfer_id = None

    try:
        with Session(model.get_engine()) as session:
            with session.begin():
                operation_id = transfer['operation_id']

                operation = session.query(model.Operation).get(operation_id)

                operation.state = transfer['next_state']

                transfer = model.Transfer(
                    tran_id=transfer['tranId'],
                    type=transfer['type'],
                    asset=transfer['asset'],
                    amount=transfer['amount'],
                    state='FILLED'
                )

                operation.transfer = transfer

            transfer_id = transfer.id

    except Exception as ex:
        print(f"Error al guardar Transferencia = {transfer}")
        print(ex)
        traceback.print_stack()

    return transfer_id

def task_operation_transfer():

    while app.running:
        try:
            transfers_dict = dict()
            transfer = dict()

            pending_transfers_dict = [row for row in model_service.get_pending_transfers()]

            for transfers_dict in pending_transfers_dict:
                transfer = binance_client.universal_transfer(type=transfers_dict['type'], asset=transfers_dict['asset'],
                                                             amount=transfers_dict['amount'])

                save_transfer({
                    **transfers_dict,
                    **transfer
                })

        except Exception as ex:
            print("Error comprar spot")
            print(transfers_dict, transfer)
            print(ex)
            traceback.print_stack()

            model_service.save_operation_state(
                transfers_dict.get('operation_id'),
                f"{transfers_dict.get('next_state')}_FAIL",
                ex
            )

if __name__ == '__main__':
    # task_transfer()

    print(model_service.get_pending_transfers())

    # operation = {'operation_id': 6, 'type': 'CMFUTURE_MAIN', 'asset': 'BCH', 'amount': 0.0554346, 'next_state': 'FUTURE_TRANSFER'}
    # transfer = {'tranId': 66485812203}
    #
    # save_transfer({
    #     **operation,
    #     **transfer
    # })
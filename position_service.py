from typing import Dict
from binance_service import binance_client
import binance_service
import model_service
import traceback

MIN_NUMBER_OF_CONTRACTS = 2
SPOT_BUY_OVERBUY_MARGIN = 1.01
OPEN_POSITION_TRANSFER_TYPE = 'MAIN_CMFUTURE'

import utils

def open_position(position_dict: Dict):
    spot_order = None
    spot_order_update = None
    spot_trade = None
    transfer = None
    future_order = None
    future_order_update = None
    future_trade = None

    try:
        spot_symbol = position_dict['spot_symbol']
        future_symbol = position_dict['future_symbol']
        buy_per_contract = position_dict['buy_per_contract']
        tick_size = position_dict['tick_size']
        base_asset = position_dict['base_asset']

        quantity_to_buy = buy_per_contract * SPOT_BUY_OVERBUY_MARGIN * MIN_NUMBER_OF_CONTRACTS
        quantity_to_buy = utils.get_quantity_rounded(quantity_to_buy, tick_size)

        spot_order = binance_client.order_market_buy(symbol=spot_symbol, quantity=quantity_to_buy)

        spot_order_id = spot_order['orderId']

        spot_trade = binance_service.get_spot_trade(spot_symbol, spot_order_id)

        transfer = binance_client.universal_transfer(type=OPEN_POSITION_TRANSFER_TYPE, asset=base_asset, amount=quantity_to_buy)

        future_order = binance_client.futures_coin_create_order(symbol=future_symbol, side="SELL", type="MARKET", quantity=MIN_NUMBER_OF_CONTRACTS)

        future_order_id = future_order['orderId']

        spot_order_update = binance_service.get_spot_order(spot_symbol, spot_order_id)

        future_order_update = binance_service.get_future_order(future_symbol, future_order_id)

        future_trade = binance_service.get_future_trade(future_symbol, future_order_id)

    except Exception as ex:
        print(ex)
        traceback.print_exc()

    return {
        'position': position_dict,
        'spot_order': spot_order,
        'spot_order_update': spot_order_update,
        'spot_trade': spot_trade,
        'transfer': transfer,
        'future_order': future_order,
        'future_order_update': future_order_update,
        'future_trade': future_trade,
    }

def save_opened_position(data_dict: Dict):
    position = data_dict['position']
    spot_order = data_dict['spot_order']
    spot_order_update = data_dict['spot_order_update']
    spot_trade = data_dict['spot_trade']
    transfer = data_dict['transfer']
    future_order = data_dict['future_order']
    future_order_update = data_dict['future_order_update']
    future_trade = data_dict['future_trade']

    base_asset = position['base_asset']
    orig_qty = spot_order['origQty'] if spot_order else None

    position_id = model_service.create_position({
        **position,
        'state': 'CREATED',
    })

    operation_id = model_service.save_operation({
        'position_id': position_id,
        'state': 'CREATED',
        'kind': 'OPEN',
        **position
    })

    spot_order_id = model_service.save_spot_order({
        'operation_id': operation_id,
        **spot_order
    })

    model_service.save_spot_order({
        'spot_order_id': spot_order_id,
        'operation_id': operation_id,
        **spot_order_update
    })

    model_service.save_spot_trade({
        'spot_order_id': spot_order_id,
        **spot_trade
    })

    model_service.save_transfer({
        'operation_id': operation_id,
        **transfer,
        'type': OPEN_POSITION_TRANSFER_TYPE,
        'asset': base_asset,
        'amount': orig_qty

    })

    future_order_id = model_service.save_future_order({
        'operation_id': operation_id,
        **future_order
    })

    model_service.save_future_order({
        'future_order_id': future_order_id,
        'operation_id': operation_id,
        **future_order_update
    })

    model_service.save_future_trade({
        'future_order_id': future_order_id,
        **future_trade
    })

def close_position(position_dict: Dict):
    spot_order = None
    spot_order_update = None
    spot_trade = None
    transfer = None
    future_order = None
    future_order_update = None
    future_trade = None

    try:
        spot_symbol = position_dict['spot_symbol']
        future_symbol = position_dict['future_symbol']
        tick_size = position_dict['tick_size']
        base_asset = position_dict['base_asset']
        contract_qty = position_dict['contract_qty']
        tansfer_amount = position_dict['tansfer_amount']
        sell_total_amount = position_dict['future_base_qty'] + position_dict['future_commission']

        future_order = binance_client.futures_coin_create_order(symbol=future_symbol, side="BUY", type="MARKET", quantity=contract_qty)

        future_order_id = future_order['orderId']

        future_trade = binance_service.get_future_trade(future_symbol, future_order_id)

        buy_net_amount = future_trade['baseQty'] - future_trade['commission']

        quantity_to_sell = tansfer_amount - sell_total_amount + buy_net_amount
        quantity_to_sell = utils.get_quantity_rounded(quantity_to_sell, tick_size)

        transfer = binance_client.universal_transfer(type=OPEN_POSITION_TRANSFER_TYPE, asset=base_asset, amount=quantity_to_sell)

        spot_order = binance_client.order_market_sell(symbol=spot_symbol, quantity=quantity_to_sell)

        spot_order_id = spot_order['orderId']

        spot_trade = binance_service.get_spot_trade(spot_symbol, spot_order_id)

        spot_order_update = binance_service.get_spot_order(spot_symbol, spot_order_id)

        future_order_update = binance_service.get_future_order(future_symbol, future_order_id)

    except Exception as ex:
        print(ex)
        traceback.print_exc()

    return {
        'position': position_dict,
        'spot_order': spot_order,
        'spot_order_update': spot_order_update,
        'spot_trade': spot_trade,
        'transfer': transfer,
        'future_order': future_order,
        'future_order_update': future_order_update,
        'future_trade': future_trade,
    }

def closed_opened_position(data_dict: Dict):
    position = data_dict['position']
    spot_order = data_dict['spot_order']
    spot_order_update = data_dict['spot_order_update']
    spot_trade = data_dict['spot_trade']
    transfer = data_dict['transfer']
    future_order = data_dict['future_order']
    future_order_update = data_dict['future_order_update']
    future_trade = data_dict['future_trade']

    base_asset = position['base_asset']
    orig_qty = spot_order['origQty'] if spot_order else None

    position_id = model_service.create_position({
        **position,
        'state': 'CLOSED',
    })

    operation_id = model_service.save_operation({
        'position_id': position_id,
        'state': 'CREATED',
        'kind': 'CLOSE',
        **position
    })

    spot_order_id = model_service.save_spot_order({
        'operation_id': operation_id,
        **spot_order
    })

    model_service.save_spot_order({
        'spot_order_id': spot_order_id,
        'operation_id': operation_id,
        **spot_order_update
    })

    model_service.save_spot_trade({
        'spot_order_id': spot_order_id,
        **spot_trade
    })

    model_service.save_transfer({
        'operation_id': operation_id,
        **transfer,
        'type': OPEN_POSITION_TRANSFER_TYPE,
        'asset': base_asset,
        'amount': orig_qty

    })

    future_order_id = model_service.save_future_order({
        'operation_id': operation_id,
        **future_order
    })

    model_service.save_future_order({
        'future_order_id': future_order_id,
        'operation_id': operation_id,
        **future_order_update
    })

    model_service.save_future_trade({
        'future_order_id': future_order_id,
        **future_trade
    })
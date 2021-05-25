from typing import Dict
from binance_service import binance_client
import binance_service
import model_service
import traceback
import json

MIN_NUMBER_OF_CONTRACTS = 2
SPOT_BUY_OVERBUY_MARGIN = 1.02
OPEN_POSITION_TRANSFER_TYPE = 'MAIN_CMFUTURE'
CLOSE_POSITION_TRANSFER_TYPE = 'CMFUTURE_MAIN'

import utils

import keys
from binance.client import Client

binance_client_position_service = Client(keys.api_key, keys.api_secret)

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

        spot_trade = binance_service.get_spot_trade(spot_symbol, spot_order_id, quantity_to_buy)

        # check real ammount to transfer based on trades
        transfer = binance_client.universal_transfer(type=OPEN_POSITION_TRANSFER_TYPE, asset=base_asset, amount=quantity_to_buy)

        future_order = binance_client.futures_coin_create_order(symbol=future_symbol, side="SELL", type="MARKET", quantity=MIN_NUMBER_OF_CONTRACTS)

        future_order_id = future_order['orderId']

        spot_order_update = binance_service.get_spot_order(spot_symbol, spot_order_id)

        future_order_update = binance_service.get_future_order(future_symbol, future_order_id)

        future_trade = binance_service.get_future_trade(future_symbol, future_order_id, MIN_NUMBER_OF_CONTRACTS)

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

    position = {
        **position,
        'contract_qty': future_order['origQty']
    }

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

    for trade in spot_trade:
        model_service.save_spot_trade({
            'spot_order_id': spot_order_id,
            **trade
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

    for trade in future_trade:
        model_service.save_future_trade({
            'future_order_id': future_order_id,
            **trade
        })

data = {'position': {'position_id': 1, 'operation_id': 1, 'future_symbol': 'DOTUSD_210625', 'future_price': 39.4567, 'spot_symbol': 'DOTUSDT', 'spot_price': 38.54, 'direct_ratio': 2.3786923328941834, 'hours': 942, 'hour_ratio': 0.0025251510964906403, 'days': 39, 'year_ratio': 22.12032360525801, 'contract_size': 10, 'buy_per_contract': 0.25344206664185204, 'tick_size': 0.001, 'base_asset': 'DOT', 'contract_qty': 2, 'transfer_amount': 0.419, 'future_base_qty': 0.416988, 'future_commission': 0.00020849, 'direct_ratio_diff': 0.6732626517707336, 'year_ratio_diff': 4.96693759469316, 'better_future_symbol': None}, 'spot_order': None, 'spot_order_update': None, 'spot_trade': None, 'transfer': None, 'future_order': {'orderId': 511229521, 'symbol': 'DOTUSD_210625', 'pair': 'DOTUSD', 'status': 'NEW', 'clientOrderId': 'TeY4zCikjfYL7CAohtUejc', 'price': '0', 'avgPrice': '0.000', 'origQty': '2', 'executedQty': '0', 'cumQty': '0', 'cumBase': '0', 'timeInForce': 'GTC', 'type': 'MARKET', 'reduceOnly': False, 'closePosition': False, 'side': 'BUY', 'positionSide': 'BOTH', 'stopPrice': '0', 'workingType': 'CONTRACT_PRICE', 'priceProtect': False, 'origType': 'MARKET', 'updateTime': 1621290515876}, 'future_order_update': None, 'future_trade': {'symbol': 'DOTUSD_210625', 'id': 5797720, 'orderId': 511229521, 'pair': 'DOTUSD', 'side': 'BUY', 'price': '39.531', 'qty': '1', 'realizedPnl': '0.03808768', 'marginAsset': 'DOT', 'baseQty': '0.25296603', 'commission': '0.00012648', 'commissionAsset': 'DOT', 'time': 1621290515876, 'positionSide': 'BOTH', 'buyer': True, 'maker': False}}


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
        transfer_amount = position_dict['transfer_amount']

        sell_future_base_qty = position_dict['future_base_qty']
        sell_future_commission = position_dict['future_commission']

        future_order = binance_client.futures_coin_create_order(symbol=future_symbol, side="BUY", type="MARKET", quantity=contract_qty)

        future_order_id = future_order['orderId']

        future_trade = binance_service.get_future_trade(future_symbol, future_order_id, contract_qty)

        buy_future_base_qty = sum([float(ft['baseQty']) for ft in future_trade])
        buy_future_commission = sum([float(ft['commission']) for ft in future_trade])

        quantity_to_sell = transfer_amount - sell_future_base_qty - sell_future_commission + buy_future_base_qty - buy_future_commission
        quantity_to_sell = utils.get_quantity_rounded(quantity_to_sell, tick_size)

        transfer = binance_client.universal_transfer(type=CLOSE_POSITION_TRANSFER_TYPE, asset=base_asset, amount=quantity_to_sell)

        spot_order = binance_client.order_market_sell(symbol=spot_symbol, quantity=quantity_to_sell)

        spot_order_id = spot_order['orderId']

        spot_trade = binance_service.get_spot_trade(spot_symbol, spot_order_id, quantity_to_sell)

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

position_to_save = {'position': {'position_id': 1, 'operation_id': 1, 'future_symbol': 'DOTUSD_210625', 'future_price': 39.4567, 'spot_symbol': 'DOTUSDT', 'spot_price': 38.54, 'direct_ratio': 2.3786923328941834, 'hours': 942, 'hour_ratio': 0.0025251510964906403, 'days': 39, 'year_ratio': 22.12032360525801, 'contract_size': 10, 'buy_per_contract': 0.25344206664185204, 'tick_size': 0.001, 'base_asset': 'DOT', 'contract_qty': 2, 'transfer_amount': 0.419, 'future_base_qty': 0.416988, 'future_commission': 0.00020849, 'direct_ratio_diff': 0.6732626517707336, 'year_ratio_diff': 4.96693759469316, 'better_future_symbol': None}, 'spot_order': None, 'spot_order_update': {'symbol': 'DOTUSDT', 'orderId': 1100432033, 'orderListId': -1, 'clientOrderId': '3PzGJUsEYOoHo3ydUDj0On', 'price': '0.00000000', 'origQty': '0.50700000', 'executedQty': '0.50700000', 'cummulativeQuoteQty': '19.61871000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1621294355935, 'updateTime': 1621294355935, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}, 'spot_trade': [{'symbol': 'DOTUSDT', 'id': 93518009, 'orderId': 1100432033, 'orderListId': -1, 'price': '38.69800000', 'qty': '0.31100000', 'quoteQty': '12.03507800', 'commission': '0.00001755', 'commissionAsset': 'BNB', 'time': 1621294355935, 'isBuyer': False, 'isMaker': False, 'isBestMatch': True}, {'symbol': 'DOTUSDT', 'id': 93518010, 'orderId': 1100432033, 'orderListId': -1, 'price': '38.69200000', 'qty': '0.19600000', 'quoteQty': '7.58363200', 'commission': '0.00001106', 'commissionAsset': 'BNB', 'time': 1621294355935, 'isBuyer': False, 'isMaker': False, 'isBestMatch': True}], 'transfer': None, 'future_order': {'orderId': 511229521, 'symbol': 'DOTUSD_210625', 'pair': 'DOTUSD', 'status': 'NEW', 'clientOrderId': 'TeY4zCikjfYL7CAohtUejc', 'price': '0', 'avgPrice': '0.000', 'origQty': '2', 'executedQty': '0', 'cumQty': '0', 'cumBase': '0', 'timeInForce': 'GTC', 'type': 'MARKET', 'reduceOnly': False, 'closePosition': False, 'side': 'BUY', 'positionSide': 'BOTH', 'stopPrice': '0', 'workingType': 'CONTRACT_PRICE', 'priceProtect': False, 'origType': 'MARKET', 'updateTime': 1621290515876}, 'future_order_update': {'orderId': 511229521, 'symbol': 'DOTUSD_210625', 'pair': 'DOTUSD', 'status': 'FILLED', 'clientOrderId': 'TeY4zCikjfYL7CAohtUejc', 'price': '0', 'avgPrice': '39.532', 'origQty': '2', 'executedQty': '2', 'cumBase': '0.50592564', 'timeInForce': 'GTC', 'type': 'MARKET', 'reduceOnly': False, 'closePosition': False, 'side': 'BUY', 'positionSide': 'BOTH', 'stopPrice': '0', 'workingType': 'CONTRACT_PRICE', 'priceProtect': False, 'origType': 'MARKET', 'time': 1621290515876, 'updateTime': 1621290516109}, 'future_trade': [{'symbol': 'DOTUSD_210625', 'id': 5797720, 'orderId': 511229521, 'pair': 'DOTUSD', 'side': 'BUY', 'price': '39.531', 'qty': '1', 'realizedPnl': '0.03808768', 'marginAsset': 'DOT', 'baseQty': '0.25296603', 'commission': '0.00012648', 'commissionAsset': 'DOT', 'time': 1621290515876, 'positionSide': 'BOTH', 'buyer': True, 'maker': False}, {'symbol': 'DOTUSD_210625', 'id': 5797721, 'orderId': 511229521, 'pair': 'DOTUSD', 'side': 'BUY', 'price': '39.532', 'qty': '1', 'realizedPnl': '0.03808128', 'marginAsset': 'DOT', 'baseQty': '0.25295963', 'commission': '0.00012647', 'commissionAsset': 'DOT', 'time': 1621290515877, 'positionSide': 'BOTH', 'buyer': True, 'maker': False}]}

def save_closed_position(data_dict: Dict):
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

    position_id = position['position_id']

    model_service.change_position_state(position_id, 'CLOSED')

    operation_id = model_service.save_operation({
        'position_id': position_id,
        'state': 'CREATED',
        'kind': 'CLOSE',
        **position,
        'operation_id': None
    })

    spot_order_id = None

    if spot_order:
        spot_order_id = model_service.save_spot_order({
            'operation_id': operation_id,
            **spot_order
        })

    if spot_order_update:
        spot_order_id = model_service.save_spot_order({
            'spot_order_id': spot_order_id,
            'operation_id': operation_id,
            **spot_order_update
        })

    for trade in (spot_trade or []):
        model_service.save_spot_trade({
            'spot_order_id': spot_order_id,
            **trade
        })

    if transfer:
        model_service.save_transfer({
            'operation_id': operation_id,
            **transfer,
            'type': CLOSE_POSITION_TRANSFER_TYPE,
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

    for trade in (future_trade or []):
        model_service.save_future_trade({
            'future_order_id': future_order_id,
            **trade
        })


if __name__ == '__main__':
    transfer_amount = 0.483

    future_trade = binance_service.get_future_trade("DOTUSD_210625", 518223677, 2)

    print(future_trade)

    realized_pnl_sum = sum([float(ft['realizedPnl']) for ft in future_trade])

    quantity_to_sell = transfer_amount + realized_pnl_sum

    quantity_to_sell = utils.get_quantity_rounded(quantity_to_sell, 0.001)

    print(quantity_to_sell)

    quantity_to_sell = utils.get_quantity_rounded(0.48566470999999994, 0.001)

    print(quantity_to_sell)


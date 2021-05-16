from typing import Dict
from datetime import datetime

import model


def sync_position(position_dict: Dict, position: model.Position = None) -> model.Position:

    if not position:
        position = model.Position()

    position.future = position_dict['future_symbol']
    position.future_price = position_dict['future_price']

    position.spot = position_dict['spot_symbol']
    position.spot_price = position_dict['spot_price']

    position.direct_ratio = position_dict['direct_ratio']

    position.hours = position_dict['hours']
    position.hour_ratio = position_dict['hour_ratio']

    position.days = position_dict['days']
    position.year_ratio = position_dict['year_ratio']

    position.contract_size = position_dict['contract_size']
    position.contract_qty = position_dict['contract_qty']

    position.buy_per_contract = position_dict['buy_per_contract']

    position.tick_size = position_dict['tick_size']
    position.base_asset = position_dict['base_asset']

    position.state = position_dict['state']

    return position

def sync_operation(operation_dict: Dict, operation: model.Operation = None) -> model.Operation:

    if not operation:
        operation = model.Operation()

    if operation_dict.get('position_id'):
        operation.position_id = operation_dict['position_id']

    operation.kind = operation_dict['kind']

    operation.future = operation_dict['future_symbol']
    operation.future_price = operation_dict['future_price']

    operation.spot = operation_dict['spot_symbol']
    operation.spot_price = operation_dict['spot_price']

    operation.direct_ratio = operation_dict['direct_ratio']

    operation.hours = operation_dict['hours']
    operation.hour_ratio = operation_dict['hour_ratio']

    operation.days = operation_dict['days']
    operation.year_ratio = operation_dict['year_ratio']

    operation.contract_size = operation_dict['contract_size']
    operation.buy_per_contract = operation_dict['buy_per_contract']

    operation.tick_size = operation_dict['tick_size']
    operation.base_asset = operation_dict['base_asset']

    operation.state = operation_dict['state']

    return operation


def sync_spot_order(spot_order_dict: Dict, spot_order: model.SpotOrder = None) -> model.SpotOrder:

    {'symbol': 'ADAUSDT', 'orderId': 1429751614, 'orderListId': -1, 'clientOrderId': '7NGE376N1RKa6tqili6xVf',
     'transactTime': 1620522698915, 'price': '0.00000000', 'origQty': '10.00000000', 'executedQty': '10.00000000',
     'cummulativeQuoteQty': '16.06700000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY',
     'fills': [{'price': '1.60670000', 'qty': '10.00000000', 'commission': '0.01000000', 'commissionAsset': 'ADA',
                'tradeId': 146553202}]}

    {'symbol': 'ADAUSDT', 'orderId': 1429751614, 'orderListId': -1, 'clientOrderId': '7NGE376N1RKa6tqili6xVf',
     'price': '0.00000000', 'origQty': '10.00000000', 'executedQty': '10.00000000',
     'cummulativeQuoteQty': '16.06700000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY',
     'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1620522698915, 'updateTime': 1620522698915,
     'isWorking': True, 'origQuoteOrderQty': '0.00000000'}

    if spot_order_dict.get('operation_id'):
        spot_order.operation_id = spot_order_dict['operation_id']

    spot_order.symbol = spot_order_dict['symbol']
    spot_order.order_id = spot_order_dict['orderId']
    spot_order.order_list_id = spot_order_dict['orderListId']
    spot_order.client_order_id = spot_order_dict['clientOrderId']
    spot_order.price = spot_order_dict['price']
    spot_order.orig_qty = spot_order_dict['origQty']
    spot_order.executed_qty = spot_order_dict['executedQty']
    spot_order.cummulative_quote_qty = spot_order_dict['cummulativeQuoteQty']
    spot_order.status = spot_order_dict['status']
    spot_order.time_in_force = spot_order_dict['timeInForce']
    spot_order.type = spot_order_dict['type']
    spot_order.side = spot_order_dict['side']

    if spot_order_dict.get('transactTime'):
        spot_order.transact_timestamp = spot_order_dict['transactTime']
        spot_order.transact_time = datetime.fromtimestamp(spot_order_dict['transactTime'] / 1000)


    if spot_order_dict.get('updateTime'):
        spot_order.update_timestamp = spot_order_dict['updateTime']
        spot_order.update_time = datetime.fromtimestamp(spot_order_dict['updateTime'] / 1000)

        spot_order.stop_price = spot_order_dict['stopPrice']
        spot_order.iceberg_qty = spot_order_dict['icebergQty']

        spot_order.timestamp = spot_order_dict['time']
        spot_order.time = datetime.fromtimestamp(spot_order_dict['time'] / 1000)

        spot_order.is_working = spot_order_dict['isWorking']
        spot_order.orig_quote_order_qty = spot_order_dict['origQuoteOrderQty']

    return spot_order

def sync_spot_trade(spot_trade_dict: Dict, spot_trade: model.SpotTrade = None,
                    spot_order_id: int = None) -> model.SpotTrade:
    # {'symbol': 'DOTUSDT', 'id': 59934629, 'orderId': 779488260, 'orderListId': -1, 'price': '36.67460000',
    #  'qty': '1.36000000', 'quoteQty': '49.87745600', 'commission': '0.00136000', 'commissionAsset': 'DOT',
    #  'time': 1617197352774, 'isBuyer': True, 'isMaker': False, 'isBestMatch': True}

    if not spot_trade:
        spot_trade = model.SpotTrade()

    if spot_trade_dict.get('spot_order_id'):
        spot_trade.spot_order_id = spot_trade_dict['spot_order_id']

    spot_trade.symbol = spot_trade_dict['symbol']
    spot_trade.binance_id = spot_trade_dict['id']
    spot_trade.order_id = spot_trade_dict['orderId']
    spot_trade.order_list_id = spot_trade_dict['orderListId']

    spot_trade.price = spot_trade_dict['price']
    spot_trade.qty = spot_trade_dict['qty']
    spot_trade.quote_qty = spot_trade_dict['quoteQty']
    spot_trade.commission = spot_trade_dict['commission']
    spot_trade.commission_asset = spot_trade_dict['commissionAsset']

    if spot_trade_dict.get('time'):
        spot_trade.timestamp = spot_trade_dict['time']
        spot_trade.time = datetime.fromtimestamp(spot_trade_dict['time'] / 1000)

    spot_trade.is_buyer = spot_trade_dict['isBuyer']
    spot_trade.is_maker = spot_trade_dict['isMaker']
    spot_trade.is_best_match = spot_trade_dict['isBestMatch']

    return spot_trade

def sync_future_order(future_order_dict, future_order=None):
    if not future_order:
        future_order = model.FutureOrder()

    if future_order_dict.get('operation_id'):
        future_order.operation_id = future_order_dict['operation_id']

    future_order.order_id = future_order_dict['orderId']
    future_order.symbol = future_order_dict['symbol']
    future_order.pair = future_order_dict['pair']
    future_order.status = future_order_dict['status']
    future_order.client_order_id = future_order_dict['clientOrderId']
    future_order.price = future_order_dict['price']
    future_order.avg_price = future_order_dict['avgPrice']
    future_order.orig_qty = future_order_dict['origQty']
    future_order.executed_qty = future_order_dict['executedQty']

    if future_order_dict.get('cumQty'):
        future_order.cum_qty = future_order_dict['cumQty']

    future_order.cum_base = future_order_dict['cumBase']
    future_order.time_in_force = future_order_dict['timeInForce']
    future_order.type = future_order_dict['type']
    future_order.reduce_only = future_order_dict['reduceOnly']
    future_order.close_position = future_order_dict['closePosition']
    future_order.side = future_order_dict['side']
    future_order.position_side = future_order_dict['positionSide']
    future_order.stop_price = future_order_dict['stopPrice']
    future_order.working_type = future_order_dict['workingType']
    future_order.price_protect = future_order_dict['priceProtect']
    future_order.orig_type = future_order_dict['origType']

    if future_order_dict.get('updateTime'):
        future_order.update_timestamp = future_order_dict['updateTime']
        future_order.update_time = datetime.fromtimestamp(future_order_dict['updateTime'] / 1000)

    return future_order

def sync_future_trade(future_trade_dict: Dict, future_trade: model.FutureTrade = None) -> model.FutureTrade:
    # {'symbol': 'DOTUSD_210625', 'id': 3873766, 'orderId': 305339166, 'pair': 'DOTUSD', 'side': 'SELL',
    #  'price': '45.940', 'qty': '1', 'realizedPnl': '0', 'marginAsset': 'DOT', 'baseQty': '0.21767523',
    #  'commission': '0.00008707', 'commissionAsset': 'DOT', 'time': 1618702550017, 'positionSide': 'BOTH',
    #  'buyer': False, 'maker': False}

    if not future_trade:
        future_trade = model.FutureTrade()

    if future_trade_dict.get('future_order_id'):
        future_trade.future_order_id = future_trade_dict['future_order_id']

    future_trade.symbol = future_trade_dict['symbol']
    future_trade.binance_id = future_trade_dict['id']
    future_trade.order_id = future_trade_dict['orderId']
    future_trade.pair = future_trade_dict['pair']
    future_trade.side = future_trade_dict['side']
    future_trade.price = future_trade_dict['price']
    future_trade.qty = future_trade_dict['qty']
    future_trade.realized_pnl = future_trade_dict['realizedPnl']
    future_trade.margin_asset = future_trade_dict['marginAsset']
    future_trade.base_qty = future_trade_dict['baseQty']
    future_trade.commission = future_trade_dict['commission']
    future_trade.commission_asset = future_trade_dict['commissionAsset']

    if future_trade_dict.get('time'):
        future_trade.timestamp = future_trade_dict['time']
        future_trade.time = datetime.fromtimestamp(future_trade_dict['time'] / 1000)

    future_trade.position_side = future_trade_dict['positionSide']
    future_trade.buyer = future_trade_dict['buyer']
    future_trade.maker = future_trade_dict['maker']

    return future_trade
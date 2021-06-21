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
    operation.contract_qty = operation_dict['contract_qty']
    operation.buy_per_contract = operation_dict['buy_per_contract']

    operation.tick_size = operation_dict['tick_size']
    operation.base_asset = operation_dict['base_asset']

    operation.state = operation_dict['state']

    operation.close_reason = operation_dict.get('close_reason')

    return operation

def get_value(dict: Dict, key1: str, key2: str, default_value = None):

    if dict.get(key1) is not None:
        return dict.get(key1)
    elif dict.get(key2) is not None:
        return dict.get(key2)
    elif default_value is not None:
        return default_value
    else:
        return None

def sync_spot_order(spot_order_dict: Dict, spot_order: model.SpotOrder = None) -> model.SpotOrder:

    {'symbol': 'ADAUSDT', 'orderId': 1429751614, 'orderListId': -1, 'clientOrderId': '7NGE376N1RKa6tqili6xVf',
     'transactTime': 1620522698915, 'price': '0.00000000', 'origQty': '10.00000000', 'executedQty': '10.00000000',
     'cummulativeQuoteQty': '16.06700000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY',
     'fills': [{'price': '1.60670000', 'qty': '10.00000000', 'commission': '0.01000000', 'commissionAsset': 'ADA',
                'tradeId': 146553202}]}

    {'e': 'executionReport', 'E': 1623109271466, 's': 'ADAUSDT', 'c': 'web_8683958899284e1e857db5a1b704b57c',
     'S': 'BUY', 'o': 'MARKET', 'f': 'GTC', 'q': '6.35000000', 'p': '0.00000000', 'P': '0.00000000', 'F': '0.00000000',
     'g': -1, 'C': '', 'x': 'TRADE', 'X': 'FILLED', 'r': 'NONE', 'i': 1694597240, 'l': '6.35000000', 'z': '6.35000000',
     'L': '1.57350000', 'n': '0.00002085', 'N': 'BNB', 'T': 1623109271463, 't': 199411622, 'I': 3576240760, 'w': False,
     'm': False, 'M': True, 'O': 1623109271463, 'Z': '9.99172500', 'Y': '9.99172500', 'Q': '10.00000000'}

    if not spot_order:
        spot_order = model.SpotOrder()

    if spot_order_dict.get('operation_id'):
        spot_order.operation_id = spot_order_dict['operation_id']

    spot_order.symbol = get_value(spot_order_dict, 'symbol', 's', spot_order.symbol)
    spot_order.order_id = get_value(spot_order_dict, 'orderId', 'i', spot_order.order_id)
    spot_order.order_list_id = get_value(spot_order_dict, 'orderListId', 'g', spot_order.order_list_id)
    spot_order.client_order_id = get_value(spot_order_dict, 'clientOrderId', 'c', spot_order.client_order_id)
    spot_order.price = get_value(spot_order_dict, 'price', 'p', spot_order.price)
    spot_order.orig_qty = get_value(spot_order_dict, 'origQty', 'q', spot_order.orig_qty)
    spot_order.executed_qty = get_value(spot_order_dict, 'executedQty', 'z', spot_order.executed_qty)
    spot_order.cummulative_quote_qty = get_value(spot_order_dict, 'cummulativeQuoteQty', 'Z', spot_order.cummulative_quote_qty)
    spot_order.status = get_value(spot_order_dict, 'status', 'X', spot_order.status)
    spot_order.time_in_force = get_value(spot_order_dict, 'timeInForce', 'f', spot_order.time_in_force)
    spot_order.type = get_value(spot_order_dict, 'type', 'o', spot_order.type)
    spot_order.side = get_value(spot_order_dict, 'side', 'S', spot_order.side)


    if get_value(spot_order_dict, 'transactTime', 'O', ):
        timestamp = get_value(spot_order_dict, 'transactTime', 'O', spot_order.transact_timestamp)

        spot_order.transact_timestamp = timestamp
        spot_order.transact_time = datetime.fromtimestamp(timestamp / 1000)

    if get_value(spot_order_dict, 'updateTime', 'T', ):
        timestamp = get_value(spot_order_dict, 'updateTime', 'T', spot_order.update_timestamp)

        spot_order.update_timestamp = timestamp
        spot_order.update_time = datetime.fromtimestamp(timestamp / 1000)


    spot_order.stop_price = get_value(spot_order_dict, 'stopPrice', 'change', spot_order.stop_price)
    spot_order.iceberg_qty = get_value(spot_order_dict, 'icebergQty', 'change', spot_order.iceberg_qty)

    if get_value(spot_order_dict, 'time', 'O', ):
        timestamp = get_value(spot_order_dict, 'time', 'O', spot_order.time)

        spot_order.time = timestamp
        spot_order.time = datetime.fromtimestamp(timestamp / 1000)

    spot_order.is_working = get_value(spot_order_dict, 'isWorking', 'w', spot_order.is_working)
    spot_order.orig_quote_order_qty = get_value(spot_order_dict, 'origQuoteOrderQty', 'Q', spot_order.orig_quote_order_qty)

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

    spot_trade.symbol = get_value(spot_trade_dict, 'symbol', 's', spot_trade.symbol)
    spot_trade.binance_id = get_value(spot_trade_dict, 'id', 't', spot_trade.binance_id)
    spot_trade.order_id = get_value(spot_trade_dict, 'orderId', 'i', spot_trade.order_id)
    spot_trade.order_list_id = get_value(spot_trade_dict, 'orderListId', 'g', spot_trade.order_list_id)

    spot_trade.price = get_value(spot_trade_dict, 'price', 'L', spot_trade.price)
    spot_trade.qty = get_value(spot_trade_dict, 'qty', 'l', spot_trade.qty)
    spot_trade.quote_qty = get_value(spot_trade_dict, 'quoteQty', 'Y', spot_trade.quote_qty)
    spot_trade.commission = get_value(spot_trade_dict, 'commission', 'n', spot_trade.commission)
    spot_trade.commission_asset = get_value(spot_trade_dict, 'commissionAsset', 'N', spot_trade.commission_asset)

    if get_value(spot_trade_dict, 'time', 'O', ):
        timestamp = get_value(spot_trade_dict, 'time', 'O', spot_trade.time)

        spot_trade.timestamp = timestamp
        spot_trade.time = datetime.fromtimestamp(timestamp / 1000)

    spot_trade.is_maker = get_value(spot_trade_dict, 'isMaker', 'm', spot_trade.is_maker)
    spot_trade.is_buyer = get_value(spot_trade_dict, 'isBuyer', 'not-implemented', spot_trade.is_buyer)

    if not spot_trade.is_maker and spot_trade.is_buyer is None:
        spot_trade.is_buyer = True

    spot_trade.is_best_match = get_value(spot_trade_dict, 'isBestMatch', 'not-implemented', spot_trade.is_best_match)

    return spot_trade

def sync_future_order(future_order_dict, future_order=None):
    if not future_order:
        future_order = model.FutureOrder()

    if future_order_dict.get('operation_id'):
        future_order.operation_id = future_order_dict['operation_id']

    future_order.order_id = get_value(future_order_dict, 'orderId', 'i', future_order.order_id)
    future_order.symbol = get_value(future_order_dict, 'symbol', 's', future_order.symbol)
    future_order.pair = get_value(future_order_dict, 'pair', 'not-implemented', future_order.pair)
    future_order.status = get_value(future_order_dict, 'status', 'X', future_order.status)
    future_order.client_order_id = get_value(future_order_dict, 'clientOrderId', 'c', future_order.client_order_id)
    future_order.price = get_value(future_order_dict, 'price', 'p', future_order.price)
    future_order.avg_price = get_value(future_order_dict, 'avgPrice', 'ap', future_order.avg_price)
    future_order.orig_qty = get_value(future_order_dict, 'origQty', 'q', future_order.orig_qty)
    future_order.executed_qty = get_value(future_order_dict, 'executedQty', 'z', future_order.executed_qty)

    future_order.cum_qty = get_value(future_order_dict, 'cumQty', 'z', future_order.cum_qty)

    contract_size = 100 if future_order.symbol.startswith('BTC') else 10

    future_order.cum_base = get_value(future_order_dict, 'cumBase', 'not-implemented', future_order.cum_base)

    if future_order.cum_base is None:
        future_order.cum_base = float(future_order.executed_qty) * contract_size / float(future_order.avg_price)

    future_order.time_in_force = get_value(future_order_dict, 'timeInForce', 'f', future_order.time_in_force)
    future_order.type = get_value(future_order_dict, 'type', 'o', future_order.type)
    future_order.reduce_only = get_value(future_order_dict, 'reduceOnly', 'R', future_order.reduce_only)
    future_order.close_position = get_value(future_order_dict, 'closePosition', 'cp', future_order.close_position)
    future_order.side = get_value(future_order_dict, 'side', 'S', future_order.side)
    future_order.position_side = get_value(future_order_dict, 'positionSide', 'ps', future_order.position_side)
    future_order.stop_price = get_value(future_order_dict, 'stopPrice', 'sp', future_order.stop_price)
    future_order.working_type = get_value(future_order_dict, 'workingType', 'wt', future_order.working_type)
    future_order.price_protect = get_value(future_order_dict, 'priceProtect', 'pP', future_order.price_protect)
    future_order.orig_type = get_value(future_order_dict, 'origType', 'ot', future_order.orig_type)

    if get_value(future_order_dict, 'updateTime', 'T',):
        timestamp = get_value(future_order_dict, 'updateTime', 'T', future_order.update_timestamp)

        future_order.update_timestamp = timestamp
        future_order.update_time = datetime.fromtimestamp(timestamp / 1000)

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

    future_trade.symbol = get_value(future_trade_dict, 'symbol', 's', future_trade.symbol)
    future_trade.binance_id = get_value(future_trade_dict, 'id', 't', future_trade.binance_id)
    future_trade.order_id = get_value(future_trade_dict, 'orderId', 'i', future_trade.order_id)
    future_trade.pair = get_value(future_trade_dict, 'pair', 'not-implemented', future_trade.pair)
    future_trade.side = get_value(future_trade_dict, 'side', 'S', future_trade.side)
    future_trade.price = get_value(future_trade_dict, 'price', 'L', future_trade.price)

    future_trade.realized_pnl = get_value(future_trade_dict, 'realizedPnl', 'rp', future_trade.realized_pnl)

    future_trade.qty = get_value(future_trade_dict, 'qty', 'q', future_trade.qty)

    future_trade.margin_asset = get_value(future_trade_dict, 'marginAsset', 'ma', future_trade.margin_asset)

    contract_size = 100 if future_trade.margin_asset == 'BTC' else 10

    base_qty = get_value(future_trade_dict, 'baseQty', 'not-implemented', future_trade.base_qty)

    if base_qty is None:
        base_qty = float(future_trade.qty) * contract_size / float(future_trade.price)

    future_trade.base_qty = base_qty

    future_trade.commission = get_value(future_trade_dict, 'commission', 'n', future_trade.commission)
    future_trade.commission_asset = get_value(future_trade_dict, 'commissionAsset', 'N', future_trade.commission_asset)

    if get_value(future_trade_dict, 'time', 'T',):
        timestamp = get_value(future_trade_dict, 'time', 'T', future_trade.timestamp)

        future_trade.timestamp = timestamp
        future_trade.time = datetime.fromtimestamp(timestamp / 1000)

    future_trade.position_side = get_value(future_trade_dict, 'positionSide', 'ps', future_trade.position_side)

    maker = get_value(future_trade_dict, 'maker', 'm', future_trade.maker)
    buyer = get_value(future_trade_dict, 'buyer', 'not-implemented', future_trade.buyer)

    if not maker and buyer is None:
        buyer = True

    future_trade.buyer = buyer
    future_trade.maker = maker

    return future_trade
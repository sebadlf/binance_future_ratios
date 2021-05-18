from binance.client import Client
from operator import itemgetter
from keys import api_key, api_secret

import traceback

import model_service

binance_client = Client(api_key, api_secret)

def filter_future_list(futures):
    filtered_futures = filter(lambda x: x['symbol'].find("_PERP") == -1, futures['symbols'])

    sorted_futures = sorted(filtered_futures, key=itemgetter("symbol"))

    return sorted_futures

def get_price_element(prices, symbol):

    price = list(filter(lambda x: x['symbol'] == symbol, prices))[0]

    return price

def get_spot_order(symbol, order_id):
    order = None

    while not order:
        try:
            order = binance_client.get_order(symbol=symbol, orderId=order_id)
        except Exception as e:
            print(e)
            traceback.print_exc()

    return order

def get_future_order(symbol, order_id):
    order = None

    while not order:
        try:
            order = binance_client.futures_coin_get_order(symbol=symbol, orderId=order_id)
        except Exception as e:
            print(e)
            traceback.print_exc()

    return order

def get_spot_trade(symbol, order_id, qty):
    trade = None

    while not trade or (abs((sum([float(t['qty']) for t in trade]) / qty) - 1) > 0.001):
        # binance_trades = binance_client.get_my_trades(symbol=symbol, fromId=from_id)
        binance_trades = binance_client.get_my_trades(symbol=symbol)

        trades = [trade for trade in binance_trades if trade['orderId'] == order_id]

        trade = trades if len(trades) else None

    return trade

def get_future_trade(symbol, order_id, qty):
    trade = None

    while not trade or sum([int(t['qty']) for t in trade]) < qty:
        # binance_trades = binance_client.get_my_trades(symbol=symbol, fromId=from_id)
        binance_trades = binance_client.futures_coin_account_trades(symbol=symbol)

        trades = [trade for trade in binance_trades if trade['orderId'] == int(order_id)]

        trade = trades if len(trades) else None

    return trade

def init_leverages():
    for symbol in model_service.get_current_futures():
        binance_client.futures_coin_change_leverage(symbol=symbol, leverage=1)

# print(binance_client.order_market_buy(symbol='ADAUSDT', quantity=10))

# print(binance_client.get_order(symbol='ADAUSDT', orderId="1429751614"))

# print(binance_client.universal_transfer(type='MAIN_CMFUTURE', asset="ADA", amount=9.99))

# print(binance_client.futures_coin_create_order(symbol="ADAUSD_210625", side="SELL", type="MARKET", quantity=1))


# print(binance_client.futures_coin_get_order(symbol="ADAUSD_210625", orderId="583939478"))


# print(binance_client.futures_coin_create_order(symbol="ADAUSD_210625", side="BUY", type="MARKET", quantity=1))

# print(binance_client.futures_coin_get_order(symbol="ADAUSD_210625", orderId="583960947"))

# print(binance_client.universal_transfer(type='CMFUTURE_MAIN', asset="ADA", amount=9.99))

# print(binance_client.get_account()['balances'])

# print(binance_client.futures_coin_account()['assets'])

#print(binance_client.universal_transfer(type='CMFUTURE_MAIN', asset="ADA", amount=9.97560693))

# [print(x) for x in binance_client.get_exchange_info()['symbols'] if x['symbol'] == 'ADAUSDT']
# [print(x['filters']) for x in binance_client.get_exchange_info()['symbols'] if x['symbol'] == 'ADAUSDT']

# print(binance_client.order_market_sell(symbol='ADAUSDT', quantity=9.97560693))

# print(binance_client.futures_coin_klines(symbol='ADAUSD_210625', interval='1m'))


# print(binance_client.order_market_buy(symbol='ADAUSDT', quantity=30))
#
# print(binance_client.order_market_sell(symbol='ADAUSDT', quantity=30))

# print(binance_client.get_order(symbol='ADAUSDT', orderId="1442982166"))

# {'symbol': 'ADAUSDT', 'orderId': 1442982166, 'orderListId': -1, 'clientOrderId': 'KsDTxPbIIJmjzJ2lTvXaYp', 'transactTime': 1620680129133, 'price': '0.00000000', 'origQty': '30.00000000', 'executedQty': '30.00000000', 'cummulativeQuoteQty': '48.87900000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'fills': [{'price': '1.62930000', 'qty': '30.00000000', 'commission': '0.00005892', 'commissionAsset': 'BNB', 'tradeId': 149870785}]}
# {'symbol': 'ADAUSDT', 'orderId': 1442982166, 'orderListId': -1, 'clientOrderId': 'KsDTxPbIIJmjzJ2lTvXaYp', 'price': '0.00000000', 'origQty': '30.00000000', 'executedQty': '30.00000000', 'cummulativeQuoteQty': '48.87900000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'stopPrice': '0.00000000', 'icebergQty': '0.00000000', 'time': 1620680129133, 'updateTime': 1620680129133, 'isWorking': True, 'origQuoteOrderQty': '0.00000000'}

if __name__ == '__main__':
    operation_id = 1

    # sell_future_order = {'orderId': 491025013, 'symbol': 'DOTUSD_210625', 'pair': 'DOTUSD', 'status': 'NEW',
    #  'clientOrderId': 'eRiA2hiJIUoWv6fWfhBxDa', 'price': '0', 'avgPrice': '0.000', 'origQty': '2', 'executedQty': '0',
    #  'cumQty': '0', 'cumBase': '0', 'timeInForce': 'GTC', 'type': 'MARKET', 'reduceOnly': False, 'closePosition': False,
    #  'side': 'SELL', 'positionSide': 'BOTH', 'stopPrice': '0', 'workingType': 'CONTRACT_PRICE', 'priceProtect': False,
    #  'origType': 'MARKET', 'updateTime': 1621043766723}
    #
    # sell_future_order_id = model_service.save_future_order({
    #     'operation_id': operation_id,
    #     **sell_future_order
    # })

    sell_future_order_id = 1

    sell_future_order_update = get_future_order("DOTUSD_210625", "491025013")

    sell_future_order_id = model_service.save_future_order({
        'future_order_id': sell_future_order_id,
        'operation_id': operation_id,
        **sell_future_order_update
    })

    sell_future_trade = get_future_trade("DOTUSD_210625", "491025013")

    sell_future_trade_id = model_service.save_future_trade({
        'future_order_id': sell_future_order_id,
        **sell_future_trade
    })

    print(sell_future_trade)
from binance.client import Client
from operator import itemgetter
from keys import api_key, api_secret

binance_client = Client(api_key, api_secret)

def filter_future_list(futures):
    filtered_futures = filter(lambda x: x['symbol'].find("_PERP") == -1, futures['symbols'])

    sorted_futures = sorted(filtered_futures, key=itemgetter("symbol"))

    return sorted_futures

def get_price_element(prices, symbol):

    price = list(filter(lambda x: x['symbol'] == symbol, prices))[0]

    return price


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

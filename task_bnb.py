from binance_service import binance_client
import time
import app
import keys
import traceback

def amount_bnb(symbol = 'BNB'):
    amount_bnb = 0
    account = binance_client.get_account()['balances']

    for i in account:
        ticker = i['asset']

        if ticker == symbol:
            amount_bnb = float(i['free'])

    return amount_bnb


def signal_buy_bnb(ticker = 'BNBUSDT', min_bnb = 150, amount_buy = 20):
    k_bnb = amount_bnb()
    price_bnb = float(binance_client.get_orderbook_ticker(symbol = ticker)['askPrice'])

    if (k_bnb*price_bnb) < min_bnb:

        amount_bnb_buy = amount_buy / price_bnb

        return amount_bnb_buy

    else:
        return False

def task_stock_bnb(quoteOrderQty = 20):
    amount_buy = signal_buy_bnb()
    if amount_buy:
        try:
            binance_client.order_market_buy(symbol = 'BNBUSDT', quoteOrderQty= quoteOrderQty)
            print('Comprados 20 usdt en bnb')

        except:
            traceback.print_exc()

    time.sleep(15)


if __name__ == '__main__':

    task_stock_bnb()

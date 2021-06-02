import math

import pandas as pd
from model import engine
import traceback

from binance_service import binance_client

def currencies():
    futures_tickers = []
    spot_tickers = []

    info = binance_client.futures_coin_exchange_info()['symbols']
    for i in info:
        if i['contractType'] != 'PERPETUAL':
            # print(i)

            future_ticker = i['symbol']
            spot_ticker = i['pair'] + 'T'
            futures_tickers.append(future_ticker)

            if spot_ticker not in spot_tickers:
                spot_tickers.append(spot_ticker)

    return futures_tickers, spot_tickers


def get_quantity_rounded(quantity, quantity_increment):

    result = 0

    if quantity_increment >= 1:
        result = int(quantity / quantity_increment) * int(quantity_increment)
    else:
        decimal_places = len(str(quantity_increment).replace("0.", ""))
        result = math.floor(quantity * 10 ** decimal_places) / (10 ** decimal_places)

    return result


def bring_data_db(ticker, k ,table, column_name_symbol = 'future_symbol'):
    query = f'select * from (select * from {table} where {column_name_symbol} = "{ticker}" order by open_time desc limit 0, {k}) data order by open_time asc'
    df = pd.read_sql(query, engine)
    df.set_index('open_time', inplace=True)
    df.drop(['future_price', 'spot_symbol', 'spot_price', 'direct_ratio', 'hours', 'hour_ratio', 'days', 'contract_size', 'buy_per_contract', 'tick_size', 'base_asset'],
            axis=1, inplace=True)

    return df


def sma(data, k, column_name = 'year_ratio'):

    try:
        data['sma'] = data[column_name].rolling(k).mean()

        return data.iloc[-1,2]

    except:
        traceback.print_exc()

        return None

def ema(data, k, column_name = 'year_ratio'):

    try:
        data['ema'] = data[column_name].ewm(span= k, adjust=False).mean()

        return data.iloc[-1,2]

    except:
        traceback.print_exc()
        return None


import math

import pandas as pd
from model import engine
import traceback


def get_quantity_rounded(quantity, quantity_increment):

    result = 0

    if quantity_increment >= 1:
        result = int(quantity / quantity_increment) * int(quantity_increment)
    else:
        decimal_places = len(str(quantity_increment).replace("0.", ""))
        result = math.floor(quantity * 10 ** decimal_places) / (10 ** decimal_places)

    return result


def bring_data_db(ticker, k ,table):
    query = f'select * from (select * from {table} where symbol = "{ticker}" order by open_time desc limit 0, {k}) data order by open_time asc'
    df = pd.read_sql(query, engine)
    df.set_index('open_time', inplace=True)
    df.drop(['id', 'open', 'high', 'low', 'volume', 'close_time', 'quote_asset_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'],
            axis=1, inplace=True)

    return df

def sma(ticker, k, table):
    k_adjusted = k
    try:
        data = bring_data_db(ticker,  k_adjusted, table)
        data['sma'] = data.close.rolling(k).mean()

        return data.iloc[-1,2]

    except:
        traceback.print_exc()
        return None

def ema(ticker, k, table):
    k_adjusted = (k*2) + 10
    try:
        data = bring_data_db(ticker,  k_adjusted, table)
        data['ema'] = data.close.ewm(span= k, adjust=False).mean()

        return data.iloc[-1,2]

    except:
        traceback.print_exc()
        return None


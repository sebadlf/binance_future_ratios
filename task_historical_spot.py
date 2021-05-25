import time
import app
import model_service
from sqlalchemy import create_engine
import utils
import keys
from datetime import datetime as dt
import traceback
import requests

import model

engine = model.get_engine()

def download_info_while(symbol, startTime, interval='4h', limit=1000):
    startTime = int(dt.strptime(startTime, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)

    last_previous_date = False

    endpoint = 'https://api.binance.com/api/v3/klines'

    md_acumulated = []

    while True:

        try:

            if not md_acumulated == []:
                startTime = md_acumulated[-1][0]  # busco ultima fecha
                md_acumulated = md_acumulated[0:-1]  # borro ultimo valor

            params = {'symbol': symbol, 'interval': interval,
                      'limit': limit,
                      'startTime': startTime,
                      # 'endTime': endTime
                      }

            r = requests.get(endpoint, params=params).json()

            if r == {'code': -1121, 'msg': 'Invalid symbol.'}:
                print(f'Invalid symbol {symbol}. No pudo bajar la md')
                break

            md_acumulated += r

            if r == []:
                print(f'fechas no validas ticker {symbol}')
                break

            if startTime == last_previous_date:
                break

            last_previous_date = startTime

        except:
            traceback.print_exc()

    return md_acumulated


def getHistorical(symbol, startTime, endTime = None, quote_currency='USDT', interval='1m', limit=1000):
    """
            Interval: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
            Limit: 500, max: 1000
            startTime: %Y-%m-%d
            endTime: %Y-%m-%d OR "hoy"
            """
    # symbol += quote_currency

    r = download_info_while(symbol, startTime, interval=interval, limit=limit)

    return r

# def currencies():
#     futures_tickers = []
#     spot_tickers = []
#
#     info = binance_client.futures_coin_exchange_info()['symbols']
#     for i in info:
#         if i['contractType'] != 'PERPETUAL':
#             # print(i)
#
#             future_ticker = i['symbol']
#             spot_ticker = i['pair'] + 'T'
#             futures_tickers.append(future_ticker)
#
#             if spot_ticker not in spot_tickers:
#                 spot_tickers.append(spot_ticker)
#
#     return futures_tickers, spot_tickers

def task_historical_spot(start_time = '2021-04-01 00:00:00'):
    engine.dispose()


    time.sleep(10)

    tickers = utils.currencies()
    tickers = tickers[1]

    if not start_time:
        start_time = dt.fromisoformat('2021-01-01')

    while app.running:
        for ticker in tickers:

            # print(ticker, end=', ')

            try:
                last_date = model_service.last_date(ticker, engine)

                if last_date:
                    model_service.del_row(last_date, engine)
                    start_time = last_date[1]

                historical_data = getHistorical(ticker, startTime= start_time)
                if historical_data != []:
                    model_service.save_historical_data_spot(engine, ticker, historical_data)
            except:
                traceback.print_exc()
                pass

            time.sleep(5)

        # print('Spot terminado, esperando 30 segundos')
        time.sleep(30)

if __name__ == '__main__':
    task_historical_spot()

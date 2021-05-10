from binance_service import binance_client
import time
import app
import model_service
from sqlalchemy import create_engine
import keys
from datetime import datetime as dt
import traceback
import requests

# def list_tickers_futures_spot(client):
#
#     futures_tickers = []
#     spot_tickers = []
#
#     info = client.futures_coin_exchange_info()['symbols']
#     for i in info:
#         if i['contractType'] != 'PERPETUAL':
#             # print(i)
#
#             future_ticker = i['symbol']
#             pair = i['pair']
#             spot_ticker = i['pair']+'T'
#             contract_type = i['contractType']
#             futures_tickers.append({'symbol': future_ticker,'pair': pair,'contractType': contract_type})
#
#             if spot_ticker not in spot_tickers:
#                 spot_tickers.append(spot_ticker)
#
#     return futures_tickers, spot_tickers
#
# tickers = list_tickers_futures_spot(binance_client)
# futures_tickers = tickers[0]
# spot_tickers = tickers[1]

# print(futures_tickers)
# print(spot_tickers)


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

def task_historical_spot(start_time = '2021-05-01 00:00:00'):

    db_connection = create_engine(keys.DB_CONNECTION)

    tickers = model_service.currencies()
    tickers = tickers[1]

    if not start_time:
        start_time = dt.fromisoformat('2021-01-01')

    while app.running:
        for ticker in tickers:

            print(ticker)

            try:
                last_date = model_service.last_date(ticker, db_connection)

                if last_date:
                    model_service.del_row(last_date, db_connection)
                    start_time = last_date[1]

                historical_data = getHistorical(ticker, startTime= start_time)
                if historical_data != []:
                    model_service.save_historical_data_spot(ticker, historical_data)
            except:
                traceback.print_exc()
                pass
        print('proceso terminado')
        time.sleep(30)

task_historical_spot()

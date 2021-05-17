from binance_service import binance_client
import time
import app
import model_service
from sqlalchemy import create_engine
import keys
from datetime import datetime as dt
import traceback
import requests
import binance.client

from task_historical_spot import currencies

def download_info_while(symbol, startTime, interval='1m', limit=1000):
    startTime = int(dt.strptime(startTime, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)

    last_previous_date = False

    # endpoint = 'https://api.binance.com/api/v3/klines'

    md_acumulated = []

    while True:

        try:

            if not md_acumulated == []:
                startTime = md_acumulated[-1][0]  # busco ultima fecha
                md_acumulated = md_acumulated[0:-1]  # borro ultimo valor

            r = binance_client.futures_coin_klines(symbol=symbol, interval= interval, limit= limit,
                                                   startTime = startTime)

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

    r = download_info_while(symbol, startTime, interval=interval, limit=limit)

    return r

def task_historical_futures(start_time = '2021-05-01 00:00:00'):

    db_connection = create_engine(keys.DB_CONNECTION)

    tickers = currencies()
    tickers = tickers[0]

    if not start_time:
        start_time = dt.fromisoformat('2021-01-01')

    while app.running:
        for ticker in tickers:

            # print(ticker, end=', ')

            try:
                last_date = model_service.last_date(ticker, db_connection, tabla= 'future_historical')

                if last_date:
                    model_service.del_row(last_date, db_connection, tabla= 'future_historical')
                    start_time = last_date[1]

                historical_data = getHistorical(ticker, startTime= start_time)

                if historical_data != []:
                    model_service.save_historical_data_futures(ticker, historical_data)

            except:
                traceback.print_exc()
                pass
        # print('Futures terminado, esperando 30 segundos')
        time.sleep(30)

if __name__ == '__main__':
    task_historical_futures()
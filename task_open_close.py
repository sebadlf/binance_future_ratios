import time
import app
import model_service
from sqlalchemy import create_engine
import utils
import keys
from datetime import datetime as dt
import traceback


def task_open_close(sma = 20, ema = 3, table = 'historical_ratios'):

    tickers = utils.currencies()
    tickers = tickers[0]

    while app.running:
        for ticker in tickers:
            print(ticker)
            sma_value = None
            ema_value = None
            resultado = None

            try:
                sma_value = utils.sma(ticker = ticker, k = sma, table= 'historical_ratios')
                ema_value = utils.ema(ticker = ticker, k = ema, table= 'historical_ratios')

                if ema_value <= sma_value:
                    resultado = 'open'

                else:
                    resultado = 'close'

            except:
                print(f'error con {ticker}')

            print(resultado)

        time.sleep(15)

task_open_close()
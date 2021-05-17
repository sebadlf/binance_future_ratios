import time
import app
from model_service import save_current_signal
import utils
import traceback
import config


def task_current_signal(sma = config.SMA, ema = config.EMA, table = 'historical_ratios'):

    tickers = utils.currencies()
    tickers = tickers[0]

    while app.running:
        for ticker in tickers:

            try:
                sma_value = utils.sma(ticker = ticker, k = sma, table= table)
                ema_value = utils.ema(ticker = ticker, k = ema, table= table)

                if ema_value <= sma_value:
                    resultado = 'open'

                else:
                    resultado = 'close'

                save_current_signal(ticker, resultado)

            except:
                traceback.print_exc()
                print(f'error con {ticker}')

        time.sleep(15)

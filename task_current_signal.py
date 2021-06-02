import time
import app
from model_service import save_current_signal
import utils
import traceback
import config


def task_current_signal(sma = config.SMA, ema = config.EMA, table = 'historical_ratios'):
    time.sleep(30)

    tickers = utils.currencies()
    tickers = tickers[0]

    if sma > ema:
        cant_rows = (sma*2) + 10
    else:
        cant_rows = (ema*2) + 10

    while app.running:
        for ticker in tickers:

            try:

                data = utils.bring_data_db(ticker = ticker, k = cant_rows, table = table)
                sma_value = utils.sma(data = data, k = sma)
                ema_value = utils.ema(data = data, k = ema)

                if ema_value and sma_value:
                    if ema_value <= sma_value:
                        resultado = 'open'

                    else:
                        resultado = 'close'

                    save_current_signal(ticker, resultado)

            except:
                traceback.print_exc()
                print(f'error con {ticker}')

        time.sleep(15)

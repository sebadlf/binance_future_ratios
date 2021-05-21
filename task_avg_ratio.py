from binance_service import binance_client
import time
import app
import model_service
import keys
import utils
import traceback

def task_avg_ratio(k = 10080):

    tickers = utils.currencies()
    tickers = tickers[0]

    i = False

    while app.running:
        for ticker in tickers:
            avg = model_service.get_data_ratio(ticker = ticker, k = k)
            model_service.save_avg_ratio(ticker, avg)

            if i:
                time.sleep(3600)

        i = True

if __name__ == '__main__':
    task_avg_ratio()
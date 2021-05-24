import time
import app
import model_service
import utils

def task_avg_ratio(field, quantity, sleep_time):

    tickers = utils.currencies()
    tickers = tickers[0]

    for ticker in tickers:
        avg = model_service.get_data_ratio(ticker=ticker, quantity=quantity)
        model_service.save_avg_ratio(ticker, field, avg)

    while app.running:
        for ticker in tickers:
            try:
                avg = model_service.get_data_ratio(ticker=ticker, quantity=quantity)
                model_service.save_avg_ratio(ticker, field, avg)
            except:
                pass

            time.sleep(sleep_time / len(tickers))

if __name__ == '__main__':
    pass

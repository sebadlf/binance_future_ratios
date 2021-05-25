import time
import app
import model_service
import model

def task_avg_ratio(tickers, field, quantity, sleep_time):
    engine = model.get_engine()
    engine.dispose()

    for ticker in tickers:
        avg = model_service.get_data_ratio(engine, ticker=ticker, quantity=quantity)
        model_service.save_avg_ratio(engine, ticker, field, avg)

    while app.running:
        for ticker in tickers:
            try:
                avg = model_service.get_data_ratio(engine, ticker=ticker, quantity=quantity)
                model_service.save_avg_ratio(engine, ticker, field, avg)
            except Exception as ex:
                print(field)
                print(ex)

            time.sleep(sleep_time / len(tickers))

if __name__ == '__main__':
    pass

import traceback
import time
import app
import model

from datetime import datetime, timedelta

engine = model.get_engine()

def task_historical_ratios_quick():
    engine.dispose()

    time.sleep(30)

    while app.running:

        current_time = datetime.utcnow()

        future_time = current_time + timedelta(seconds=10)

        seconds = future_time.timetuple().tm_sec

        future_time = future_time.replace(second=int(seconds / 10) * 10)

        difference = future_time - current_time

        time.sleep(difference.total_seconds())

        try:
            with engine.begin() as connection:
                query = f"""
                insert historical_ratios_quick(
                    time,
                    future_symbol,
                    spot_symbol,
                    hours,
                    days,
                    future_price,
                    spot_price,
                    direct_ratio,
                    hour_ratio,
                    year_ratio
                ) select 
                    now(),
                    future_symbol,
                    spot_symbol,
                    hours,
                    days,
                    future_price,
                    spot_price,
                    direct_ratio,
                    hour_ratio,
                    year_ratio	 
                from
                    current_ratios
                """

                connection.execute(query)

        except Exception as ex:
            print(ex)
            traceback.print_stack()

if __name__ == '__main__':
    model.create_tables()
    task_historical_ratios_quick()
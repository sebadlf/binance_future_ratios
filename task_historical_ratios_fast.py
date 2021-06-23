import traceback
import time
import app
import model

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

engine = model.get_engine()

def task_historical_ratios_fast():
    engine.dispose()

    time.sleep(30)

    while app.running:

        current_time = datetime.utcnow()

        future_time = current_time + timedelta(seconds=10)

        seconds = future_time.timetuple().tm_sec

        future_time = future_time.replace(second=int(seconds / 10) * 10).replace(microsecond=0)

        difference = future_time - current_time

        time.sleep(difference.total_seconds())

        try:

            with Session(engine) as session, session.begin():
                current_ratios = session.query(model.CurrentRatiosOpen).all()

                for current_ratio in current_ratios:
                    ratio = model.HistoricalRatiosQuick()
                    session.add(ratio)

                    ratio.time = future_time
                    ratio.future_symbol = current_ratio.future_symbol
                    ratio.spot_symbol = current_ratio.spot_symbol
                    ratio.hours = current_ratio.hours
                    ratio.days = current_ratio.days
                    ratio.future_price = current_ratio.future_price
                    ratio.spot_price = current_ratio.spot_price
                    ratio.direct_ratio = current_ratio.direct_ratio
                    ratio.hour_ratio = current_ratio.hour_ratio
                    ratio.year_ratio = current_ratio.year_ratio

        except Exception as ex:
            print(ex)
            traceback.print_stack()

if __name__ == '__main__':
    model.create_tables()
    task_historical_ratios_quick()
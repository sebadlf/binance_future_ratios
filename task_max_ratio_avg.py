import time
import app

import utils
import traceback
import config

from model import engine
import pandas as pd
import time
from model_service import save_max_historical_ratio

def task_max_historical_ratio(table='historical_ratios', k=43200):

    while app.running:

        query = f'select open_time, max(year_ratio) max_year_ratio from {table} where' \
                f' direct_ratio > 0.6 group by open_time order by open_time desc limit 0, {k}'

        df = pd.read_sql(query, engine).sort_values(by='open_time', ascending=True)
        df['ema'] = df['max_year_ratio'].ewm(span=(k), adjust=False).mean()
        resultado = df.iloc[-1]

        save_max_historical_ratio(resultado['open_time'], resultado['ema'])

        time.sleep(25)

prueba = task_max_historical_ratio()
print(prueba)



"""
ESTRUCTURA

DATOS
- ratios por hora directos
- condicion de entrada (ver codigo de seba)
- condicion de salida (sensibilidad en 2 emas, corta y larga)

1 - BAJA DE DATOS (query que baja los datos y los pasa a un data frame, ordenados de menor a mayor)

2 - AGREGADO DE INDICADORES

3 - AGREGADO DE ALERTAS COMPRA Y VENTA

4 - FILTRO DE TRADES

5 - ANALISIS DE SENSIBILIDAD CUAL DIO MEJOR RESULTADO

6 - GRAFICAR EL MEJOR RESULTADO

"""

import time
import app
import model_service
import model
import utils

# PRIMERO VOY A TOMAR LA BAJA DE DATOS QUE YA TENGO

engine = model.get_engine()
engine.dispose()

tickers = utils.currencies()
tickers = tickers[0]

for ticker in tickers:


print(tickers)


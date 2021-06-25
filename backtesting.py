import time
import app
import model_service
import model
import utils
import backtesting_utils

import traceback
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.options.display.max_rows = 30
pd.options.display.max_columns = 20

engine = model.get_engine()
engine.dispose()

### SETEO DATOS ###
###################

k_min = 20000
k_seg = 100000
averages = [
    # 10080,
    1440, 360, 60, 10]
# sma = [6, 8, 10]
# ema = [28, 30, 40, 50, 60, 90]
sma = [27, 30, 33]
ema = [8, 9, 10]

condition_cruce_buy = [-1]
condition_cruce_sell = [1]

condition_buy_year_ratio = [0.45]
condition_sell_direct_ratio = [10]

# TICKERS
# tickers = utils.currencies()
# tickers = tickers[0]

tickers = ['BTCUSD_210924', 'ETHUSD_210924', 'ADAUSD_210924', 'LINKUSD_210924',
           'BCHUSD_210924', 'DOTUSD_210924', 'XRPUSD_210924', 'LTCUSD_210924', 'BNBUSD_210924']

for ticker in tickers:
    start_time_1 = time.time()

    results = []

    # DATA
    data_min = utils.bring_data_db(ticker, k=k_min, table='historical_ratios')
    data_seg = utils.bring_data_db_seg(ticker, k=k_seg, table='historical_ratios_quick')

    data_seg.to_excel('prueba.xlsx')

    # SETEO DATA FRAME LARGO
    data_min = backtesting_utils.alerta_con_avg(data_min, averages)

    # ITERO DISTINTAS EMA Y SMA (por ahora solo para el corto, cuando agregue el largo lo anterior t endria que ir dentro
    for k_ema in ema:
        for k_sma in sma:
            data_seg = backtesting_utils.alerta_con_dif_emas(data_seg, k_ema, k_sma, condition_cruce_buy, condition_cruce_sell)

            # CONCATENO DF
            df_concat = backtesting_utils.concat_largo_corto(data_min, data_seg)

            # OPERACOINES
            operations_list = backtesting_utils.operations(df_concat, condition_buy_year_ratio, condition_sell_direct_ratio)

            # TRADES
            trades = backtesting_utils.trades(operations_list)
            if trades is None:
                print(f'no hubieron trades con ema de {k_ema} y sma de {k_sma}')
                continue

            print(trades)
            # ACUMULANDO RESULTADOS FINALES DE CADA ESTRATEGIA
            results.append(backtesting_utils.accum_trades(trades, k_ema, k_sma))


    # DATA FRAME DE RESULTADOS
    df_results = backtesting_utils.df_results(results)

    print(df_results)

    ### PLOTS ###
    #############
    ema_best = df_results.iloc[0, 0]
    sma_best = df_results.iloc[0, 1]

    # HAGO OPERACIONES DE NUEVO
    data_seg = backtesting_utils.alerta_con_dif_emas(data_seg, ema_best, sma_best, condition_cruce_buy, condition_cruce_sell)
    df_concat = backtesting_utils.concat_largo_corto(data_min, data_seg)
    operations_list = backtesting_utils.operations(df_concat, condition_buy_year_ratio, condition_sell_direct_ratio)
    trades = backtesting_utils.trades(operations_list)

    # print(trades)
    # print(data_seg)
    df_buy = trades.copy().set_index('open_time')
    df_buy.drop(['close_time', 'direct_ratio_sell', 'time', 'return_trade', 'return_accu'], axis=1, inplace=True)
    df_buy.index.name = 'time'

    df_sell = trades.copy().set_index('close_time')
    df_sell.drop(['open_time', 'direct_ratio_buy', 'time', 'return_trade', 'return_accu'], axis=1, inplace=True)
    df_sell.index.name = 'time'

    # concateno data frames
    data_seg_trades = pd.concat([data_seg, df_buy, df_sell], axis=1)
    data_seg_trades.drop(['year_ratio', 'alerta_seg'], axis=1, inplace=True)
    data_seg_trades['direct_ratio_buy'] = data_seg_trades['direct_ratio_buy'] * 1.05
    data_seg_trades['direct_ratio_sell'] = data_seg_trades['direct_ratio_sell'] * 0.95


    # SETEO
    plt.figure(figsize=(40, 7)).suptitle(ticker, fontsize=16)
    plt.grid(which='major', axis='y', color='black', lw=1, alpha=0.4)
    plt.minorticks_on()
    plt.grid(which='minor', axis='both', color='black', alpha=0.15)

    # SMA Y EMA PARA GRAFICAR
    backtesting_utils.sma_backtesting(data_seg_trades, sma_best, 'direct_ratio')
    backtesting_utils.ema_backtesting(data_seg_trades, ema_best, 'direct_ratio')
    # print(data_seg_trades)
    # data_seg_trades.dropna(inplace=True)

    f1 = plt.plot(data_seg_trades['direct_ratio'], c='k', ls='-', lw=1)
    f2 = plt.plot(data_seg_trades['sma_' + str(sma_best)], c='b', ls='-.', lw=0.2)
    f3 = plt.plot(data_seg_trades['ema_' + str(ema_best)], c='g', ls='-.', lw=0.2)

    plt.legend(['Ratio'], loc='lower right')
    plt.plot(data_seg_trades.index, data_seg_trades['direct_ratio_buy'], "v", markersize=10, c='g')
    plt.plot(data_seg_trades.index, data_seg_trades['direct_ratio_sell'], "^", markersize=10, c='r')

    plt.legend(['Ratio', 'SMA', 'EMA'], loc='lower right')

    plt.show()

    end = time.time()

    # print (df_results)
    print(end - start_time_1)

    break









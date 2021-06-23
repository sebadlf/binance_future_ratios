import pandas as pd
import traceback
import numpy as np


def sma_backtesting(data, k, column_name='year_ratio'):
    try:
        data['sma_' + str(k)] = data[column_name].rolling(k).mean()
        return data

    except:
        traceback.print_exc()
        return print('error en sma')


def ema_backtesting(data, k, column_name='year_ratio'):
    try:
        data['ema_' + str(k)] = data[column_name].ewm(span=k, adjust=False).mean()

        return data

    except:
        traceback.print_exc()
        return print('error en ema')


def dif_ema_sma(df, k_ema, k_sma):

    df['ratio_ema_' + str(k_ema) + '_sma_' + str(k_sma)] = (df['direct_ratio'].ewm(span=k_ema, adjust=False).mean() / df['direct_ratio'].rolling(k_sma).mean() - 1) * 100

    return df


def alerta_con_avg(df, averages):
    for avg in averages:
        sma_backtesting(data=df, k=avg)

    df.dropna(inplace=True)

    # ALERTA A LA DATA POR MINUTO
    df['alerta_min'] = np.where(
        df['sma_' + str(averages[0])] < df['sma_' + str(averages[1])], np.where(
            df['sma_' + str(averages[1])] < df['sma_' + str(averages[2])], np.where(
                df['sma_' + str(averages[2])] < df['sma_' + str(averages[3])], 'compra', 'venta'),
            'venta'),
        'venta')

    # BORRO LOS AVG (YA NO ME INTERESAN)
    for i in averages:
        df.drop(['sma_' + str(i)], axis=1, inplace=True)

    df.drop(['future_symbol', 'year_ratio'], axis=1, inplace=True)

    return df


def alerta_con_dif_emas(df, k_ema, k_sma, condition_cruce_buy, contidion_cruce_sell):
    # Dif ema/sma
    dif_ema_sma(df, k_ema, k_sma)

    # ALERTA DATA POR SEGUNDO
    df['alerta_seg'] = np.where(
        df['ratio_ema_' + str(k_ema) + '_sma_' + str(k_sma)] <= condition_cruce_buy[0],
        'compra', np.where(
            df['ratio_ema_' + str(k_ema) + '_sma_' + str(k_sma)] >= contidion_cruce_sell[0],
            'venta', 'nada'))

    df.drop(['ratio_ema_' + str(k_ema) + '_sma_' + str(k_sma)], axis=1, inplace=True)

    return df


def concat_largo_corto(data_min, data_seg):
    data_concat = pd.concat([data_min, data_seg], axis=1)
    data_concat['alerta_min'] = data_concat['alerta_min'].fillna(method='ffill').dropna()
    # data_concat.dropna(inplace=True)
    data_concat.reset_index(inplace=True)
    data_concat.dropna(inplace=True)

    return data_concat


def operations(df, condition_buy_year_ratio, condition_sell_direct_ratio):
    operations = {'open_time': False, 'close_time': False, 'direct_ratio_buy': False, 'direct_ratio_sell': False}
    result = []

    k_rows = len(df)

    for i in range(k_rows):

        fila = df.iloc[i]
        time_op, alerta_min, direct_ratio, year_ratio, alerta_seg = fila[0], fila[1], fila[3], fila[4], fila[5]
        # print(time, alerta_min, direct_ratio, year_ratio, alerta_seg)

        if not operations['open_time'] and \
                alerta_min == 'compra' and \
                alerta_seg == 'compra' and \
                direct_ratio >= condition_buy_year_ratio[0]:
            operations['open_time'], operations['direct_ratio_buy'] = time_op, (direct_ratio - 0.15)
            print(operations)

        elif operations['open_time'] and \
                alerta_seg == 'venta' and \
                ((direct_ratio / operations['direct_ratio_buy'] - 1 + 0.15) * -100) >= condition_sell_direct_ratio[0]:

            operations['close_time'], operations['direct_ratio_sell'] = time_op, (direct_ratio + 0.15)

            result.append(operations)

            # reseteo diccionario
            operations = {'open_time': False, 'close_time': False, 'direct_ratio_buy': False,
                          'direct_ratio_sell': False}

    return result


def trades(list):
    df_trades = pd.DataFrame(list)
    try:
        df_trades['time'] = df_trades['close_time'] - df_trades['open_time']
        df_trades['return_trade'] = (df_trades['direct_ratio_buy'] - df_trades['direct_ratio_sell'] - 0.3)
        # df_trades['return_trade'] = df_trades['rdo'] / df_trades['direct_ratio_buy']
        df_trades['return_accu'] = np.cumprod(1 + df_trades['return_trade'].values) - 1

        return df_trades

    except:
        return None


def accum_trades(df, k_ema, k_sma):
    fila = df.iloc[(len(df) - 1)]
    dictionary_for_operations = {'ema': k_ema, 'sma': k_sma, 'time_avg': False, 'return': fila[6]}

    return dictionary_for_operations


def df_results(results):
    df = pd.DataFrame(results)
    df.sort_values(['return'], ascending=False, inplace=True)

    return df

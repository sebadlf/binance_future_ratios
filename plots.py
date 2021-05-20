import matplotlib.pyplot as plt
import utils

ticker = 'DOTUSD_210625'
k_sma = 5
k_ema = 5

data = utils.bring_data_db(ticker, 10000000, table = 'historical_ratios')
print(data)
data.drop(['future_symbol'], axis=1, inplace= True)

data = data.loc[(data.index > '2021-05-19 09:00:00') & (data.index < '2021-05-19 12:00:00')]

print(data)

# medias
data['sma'] = data['year_ratio'].rolling(k_sma).mean()
data['ema'] = data['year_ratio'].ewm(span= k_ema, adjust=False).mean()


# tamaño
plt.figure(figsize= (20,7)).suptitle(ticker, fontsize = 16)

# grilla
plt.grid(which= 'major', axis= 'y', color= 'black', lw= 1, alpha= 0.4)
plt.minorticks_on()
plt.grid(which= 'minor', axis= 'both', color= 'black', alpha= 0.15)

# medias
f1 = plt.plot(data['year_ratio'], c= 'k', ls= '-', lw= 1.5)
f2 = plt.plot(data['sma'], c= 'b', ls= 'solid', lw= 0.5)
f3 = plt.plot(data['ema'], c= 'r', ls= 'solid', lw= 0.5)
plt.legend(['Ratio', 'SMA', 'EMA'], loc ='lower right')

plt.show()
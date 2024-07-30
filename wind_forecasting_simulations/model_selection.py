import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from statsmodels.tsa.stattools import adfuller
from numpy import log
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt

df = pd.read_csv('raspberry/data/wind_data/25-09-23--16-49/25-09-23--16-49_N_10.csv')


result = adfuller(df.Wind_Speed.dropna())
print('ADF Statistic: %f' % result[0])
print('p-value: %f' % result[1])



plot_acf(df.Wind_Speed, lags=50)
plot_acf(df.Wind_Speed.diff().dropna(), lags=50)
plot_acf(df.Wind_Speed.diff().diff().dropna(), lags=50)

plot_pacf(df.Wind_Speed, lags=50)
plot_pacf(df.Wind_Speed.diff(), lags=50)
plot_pacf(df.Wind_Speed.diff().diff().dropna(), lags=50)

plt.show()
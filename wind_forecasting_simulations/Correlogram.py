import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from statsmodels.tsa.stattools import adfuller
from pandas.plotting import register_matplotlib_converters
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.arima.model import ARIMA
register_matplotlib_converters()
from time import time
import matplotlib.dates as mdates

#read data
df_wind = pd.read_csv('raspberry/anemometer/wind_data/25-09-23--16-49/25-09-23--16-49_2Hz.csv')

#set index
df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="500L")

windspeed = pd.Series()
windspeed_minus_1 = pd.Series()

for x in range(100):
    for t in range(2000):
        windspeed[df_wind.index[t]] = df_wind.Wind_Speed[t]
        windspeed_minus_1[df_wind.index[t]] = df_wind.Wind_Speed[t-x]
    
    print(windspeed)
    print(windspeed_minus_1)
    
    plt.figure(figsize=(10,4))
    plt.scatter(windspeed, windspeed_minus_1)
    plt.title(f'W_t against W_t-{str(t)}', fontsize=20)
    plt.xlabel(f'W_t-{str(t)}', fontsize=16)
    plt.ylabel('W_t', fontsize=16)
    
plt.show()
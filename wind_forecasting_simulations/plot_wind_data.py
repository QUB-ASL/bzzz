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

plt.figure(figsize=(10,4))
plt.plot(df_wind.Wind_Speed)
plt.title('Wind speed over Time', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

acf_plot = plot_acf(df_wind.Wind_Speed, lags=50)
pacf_plot = plot_pacf(df_wind.Wind_Speed, lags=50)


plt.figure(figsize=(10,4))
plt.plot(df_wind.U_axis)
plt.title('Wind speed over Time', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

acf_plot = plot_acf(df_wind.U_axis, lags=50)
pacf_plot = plot_pacf(df_wind.U_axis, lags=50)


plt.figure(figsize=(10,4))
plt.plot(df_wind.V_axis)
plt.title('Wind speed over Time', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

acf_plot = plot_acf(df_wind.V_axis, lags=50)
pacf_plot = plot_pacf(df_wind.V_axis, lags=50)


plt.figure(figsize=(10,4))
plt.plot(df_wind.W_axis)
plt.title('Wind speed over Time', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

acf_plot = plot_acf(df_wind.W_axis, lags=50)
pacf_plot = plot_pacf(df_wind.W_axis, lags=50)

plt.show()
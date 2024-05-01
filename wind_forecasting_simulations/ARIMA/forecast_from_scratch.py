import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from time import time
import matplotlib.dates as mdates
import csv


## Read data
df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--16-49/25-09-23--16-49_N_10.csv')

## Set index
df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="25L")

## Plot Wind Speed against time
plt.figure(figsize=(10,4))
plt.plot(df_wind.Wind_Speed)
plt.title('combined Wind speed over Time', fontsize=20)
plt.ylabel('Wind Speed m/s', fontsize=16)

ar1 = 1.572654
ar2 = -1.193433
ar3 = 0.9085445
ar4 = -0.5089323
ar5 = 0.2081693
ma1 = -0.0713252
ma2 = 0.9297537
ma3 = 0.0202807
ma4 = 0.8987153
ma5 = -0.0014764
ma6 = 0.9206075
ma7 = 0.0372892
ma8 = 0.8512221

y = np.array([1.394,1.356,1.32,1.276,1.179,1.11,1.053,1.007])
y_hat = np.array([1.394,1.356,1.32,1.276,1.179,1.11,1.053,1.007])
e = np.array([0.,0.,0.,0.,0.,0.,0.,0.])
forecast_cache = np.array([1.007,1.053,1.11,1.179,1.276,1.32,1.356,1.394])
t_plus_x_cache = np.array([1.007,1.053,1.11,1.179,1.276,1.32,1.356,1.394])

for x in range(10):
    forecast_cache = np.append(forecast_cache,df_wind.Wind_Speed[x+8])
    t_plus_x_cache = np.append(t_plus_x_cache,df_wind.Wind_Speed[x+8])

for x in range(1000):

    y = np.roll(y,1)
    y[0] = df_wind.Wind_Speed[x+8]

    y_temp = y
    e_temp = e 

    ARMA = (ar1*(y[0]) + ar2*(y[1]) + ar3*(y[2]) + ar4*(y[3]) + ar5*(y[4]) 
            + ma1*(e[0]) + ma2*(e[1]) + ma3*(e[2]) + ma4*(e[3]) 
            + ma5*(e[4]) + ma6*(e[5]) + ma7*(e[6]) + ma8*(e[7]))
    
    y_hat = np.roll(y_hat,1)
    y_hat[0] = ARMA

    for z in range(10):
        ARMA2 = (ar1*(y_temp[0]) + ar2*(y_temp[1]) + ar3*(y_temp[2]) + ar4*(y_temp[3]) + ar5*(y_temp[4]) 
            + ma1*(e_temp[0]) + ma2*(e_temp[1]) + ma3*(e_temp[2]) + ma4*(e_temp[3]) 
            + ma5*(e_temp[4]) + ma6*(e_temp[5]) + ma7*(e_temp[6]) + ma8*(e_temp[7]))
        # print(ARMA2)
        y_temp = np.roll(y_temp,1)
        y_temp[0] = ARMA2
        e_temp = np.roll(e_temp,1)
        e_temp[0] = 0

    forecast_cache = np.append(forecast_cache,ARMA2)
    e = y - y_hat
    t_plus_x_cache = np.append(t_plus_x_cache,df_wind.Wind_Speed[x])

forecast = {'forecast': forecast_cache}
t_plus_x = {'t_plus_x': t_plus_x_cache}

df = pd.DataFrame(forecast)
df.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2[1017], freq="25L")
df['real_wind'] = df_wind.Wind_Speed.values[0:1018]
df['residuals'] = df.real_wind - df.forecast
df['t_plus_x'] = t_plus_x_cache
df.to_csv("data.csv")

## Plot Residuals against time
plt.figure(figsize=(10,4))
plt.plot(df.residuals)
plt.title('Residuals from ARIMA Model', fontsize=20)
plt.ylabel('Residual', fontsize=16)
plt.axhline(0, color='r', linestyle='--', alpha=0.2)

## Plot predictions and test data against time
plt.figure(figsize=(10,4))
plt.plot(df_wind.Wind_Speed)
plt.plot(df.forecast)
plt.legend(('Data', 'Predictions'), fontsize=16)
plt.title('Wind Prediction', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

plt.show()

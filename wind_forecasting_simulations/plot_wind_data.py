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

def plot_wind_data(U: bool,
                   V: bool,
                   W: bool,
                   file_name_1,
                   data_freq_1,
                   acf_pacf_1: bool,
                   file_name_2=None,
                   data_freq_2=None,
                   acf_pacf_2: bool=False,
                   file_name_3=None,
                   data_freq_3=None,
                   acf_pacf_3: bool=False):
    #read data
    df_wind = pd.read_csv(file_name_1)
    if file_name_2 is not None:
        df_wind_2 = pd.read_csv(file_name_2)
    if file_name_3 is not None:
        df_wind_3 = pd.read_csv(file_name_3)

    index_freq_1 = 1000/data_freq_1
    if data_freq_2 is not None:
        index_freq_2 = 1000/data_freq_2
    if data_freq_3 is not None:
        index_freq_3 = 1000/data_freq_3
    #set index
    df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq=f'{index_freq_1}L')
    if file_name_2 is not None and data_freq_2 is not None:
        df_wind_2.index = pd.date_range(df_wind_2.Index_2[0], df_wind_2.Index_2.iloc[-1], freq=f'{index_freq_2}L')
    if file_name_3 is not None and data_freq_3 is not None:
        df_wind_3.index = pd.date_range(df_wind_3.Index_2[0], df_wind_3.Index_2.iloc[-1], freq=f'{index_freq_3}L')

    plt.figure(figsize=(10,4))
    plt.plot(df_wind.Wind_Speed)
    if file_name_2 is not None:
        plt.plot(df_wind_2.Wind_Speed)
    if file_name_3 is not None:
        plt.plot(df_wind_3.Wind_Speed)
    plt.title('combined Wind speed over Time', fontsize=20)
    plt.ylabel('Wind Speed', fontsize=16)

    if acf_pacf_1 is True:
        plot_acf(df_wind.Wind_Speed, lags=50)
        plot_pacf(df_wind.Wind_Speed, lags=50)
    if acf_pacf_2 is True:
        plot_acf(df_wind_2.Wind_Speed, lags=50)
        plot_pacf(df_wind_2.Wind_Speed, lags=50)
    if acf_pacf_3 is True:
        plot_acf(df_wind_3.Wind_Speed, lags=50)
        plot_pacf(df_wind_3.Wind_Speed, lags=50)


    if U is True:
        plt.figure(figsize=(10,4))
        plt.plot(df_wind.U_axis)
        if file_name_2 is not None:
            plt.plot(df_wind_2.U_axis)
        if file_name_3 is not None:
            plt.plot(df_wind_3.U_axis)
        plt.title('U Wind speed over Time', fontsize=20)
        plt.ylabel('Wind Speed', fontsize=16)
    
        if acf_pacf_1 is True:
            plot_acf(df_wind.U_axis, lags=50)
            plot_pacf(df_wind.U_axis, lags=50)
        if acf_pacf_2 is True:
            plot_acf(df_wind_2.U_axis, lags=50)
            plot_pacf(df_wind_2.U_axis, lags=50)
        if acf_pacf_3 is True:
            plot_acf(df_wind_3.U_axis, lags=50)
            plot_pacf(df_wind_3.U_axis, lags=50)


    if V is True:
        plt.figure(figsize=(10,4))
        plt.plot(df_wind.V_axis)
        if file_name_2 is not None:
            plt.plot(df_wind_2.V_axis)
        if file_name_3 is not None:
            plt.plot(df_wind_3.V_axis)
        plt.title('V Wind speed over Time', fontsize=20)
        plt.ylabel('Wind Speed', fontsize=16)
    
        if acf_pacf_1 is True:
            plot_acf(df_wind.V_axis, lags=50)
            plot_pacf(df_wind.V_axis, lags=50)
        if acf_pacf_2 is True:
            plot_acf(df_wind_2.V_axis, lags=50)
            plot_pacf(df_wind_2.V_axis, lags=50)
        if acf_pacf_3 is True:
            plot_acf(df_wind_3.V_axis, lags=50)
            plot_pacf(df_wind_3.V_axis, lags=50)

    
    if W is True:
        plt.figure(figsize=(10,4))
        plt.plot(df_wind.W_axis)
        if file_name_2 is not None:
            plt.plot(df_wind_2.W_axis)
        if file_name_3 is not None:
            plt.plot(df_wind_3.W_axis)
        plt.title('W Wind speed over Time', fontsize=20)
        plt.ylabel('Wind Speed', fontsize=16)
    
        if acf_pacf_1 is True:
            plot_acf(df_wind.W_axis, lags=50)
            plot_pacf(df_wind.W_axis, lags=50)
        if acf_pacf_2 is True:
            plot_acf(df_wind_2.W_axis, lags=50)
            plot_pacf(df_wind_2.W_axis, lags=50)
        if acf_pacf_3 is True:
            plot_acf(df_wind_3.W_axis, lags=50)
            plot_pacf(df_wind_3.W_axis, lags=50)

    return 0

plot_wind_data(U=True,
               V=True,
               W=True,
               file_name_1='raspberry/data/wind_data/25-09-23--16-49/25-09-23--16-49.csv',
               data_freq_1=40,
               acf_pacf_1=True,
               file_name_2='raspberry/data/wind_data/25-09-23--16-49/25-09-23--16-49_N_5.csv',
               data_freq_2=40,
               acf_pacf_2=False,
               file_name_3='raspberry/data/wind_data/25-09-23--16-49/25-09-23--16-49_N_10.csv',
               data_freq_3=40,
               acf_pacf_3=False)
plt.show()
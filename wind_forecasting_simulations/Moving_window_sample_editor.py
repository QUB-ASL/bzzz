import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

def MovingAverageFilter(file_name,
                        number_samples):

    #read data
    df_wind = pd.read_csv(f'{file_name}.csv')
    res = df_wind
    
    #set index
    df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="200L")
    
    # Calculating mean
    res['Wind_Speed'] = df_wind.Wind_Speed.rolling(number_samples).mean().round(4)
    res['Wind_Speed_2D'] = df_wind.Wind_Speed_2D.rolling(number_samples).mean().round(4)
    res['H_direction'] = df_wind.H_direction.rolling(number_samples).mean().round(4)
    res['V_direction'] = df_wind.V_direction.rolling(number_samples).mean().round(4)
    res['U_axis'] = df_wind.U_axis.rolling(number_samples).mean().round(4)
    res['V_axis'] = df_wind.V_axis.rolling(number_samples).mean().round(4)
    res['W_axis'] = df_wind.W_axis.rolling(number_samples).mean().round(4)
    
    #set index
    res.index = pd.date_range(res.Index_2[0], res.Index_2.iloc[-1], freq="200L")
    
    #save file
    res.to_csv(f'{file_name}_N_{str(number_samples)}.csv', index=False)

    plt.figure(figsize=(10,4))
    plt.plot(df_wind.Wind_Speed)
    plt.plot(res.Wind_Speed)
    plt.title('Wind speed over Time', fontsize=20)
    plt.ylabel('Wind Speed', fontsize=16)

    plt.show() 

MovingAverageFilter(file_name='raspberry/data/wind_data/25-09-23--16-49/25-09-23--16-49_5Hz',
                    number_samples=4)
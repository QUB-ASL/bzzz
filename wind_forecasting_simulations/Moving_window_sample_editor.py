import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

def MovingAverageFilter(file_name,
                        number_samples):

    #read data
    df_wind = pd.read_csv(f'{file_name}.csv')
    
    #set index
    df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="25L")
    
    # Calculating mean
    res = df_wind.rolling(number_samples).mean().round(4)
    
    res['Index'] = df_wind.Index.values
    res['Index_2'] = df_wind.Index_2.values
    res['Date_Time'] = df_wind.Date_Time.values
    
    res = res[["Index", "Index_2", "Date_Time", "Wind_Speed", "Wind_Speed_2D", "H_direction", "V_direction", "U_axis", "V_axis", "W_axis"]]
    
    #set index
    res.index = pd.date_range(res.Index_2[0], res.Index_2.iloc[-1], freq="25L")
    
    #save file
    res.to_csv(f'{file_name}_N_{str(number_samples)}.csv', index=False)

    plt.figure(figsize=(10,4))
    plt.plot(df_wind.Wind_Speed)
    plt.plot(res.Wind_Speed)
    plt.title('Wind speed over Time', fontsize=20)
    plt.ylabel('Wind Speed', fontsize=16)

    plt.show() 

MovingAverageFilter(file_name='raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23',
                    number_samples=10)
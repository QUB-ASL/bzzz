import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

def DataEditor(file_name):

    #read data
    df_wind = pd.read_csv(f'{file_name}.csv')
    
    res = pd.DataFrame({'A' : []})

    res['Index'] = df_wind['index']
    res['Date_Time'] = df_wind['date_time']
    res['Wind_Speed'] = df_wind['wind_speed']
    res['Wind_Speed_2D'] = df_wind['wind_speed_2D']
    res['H_direction'] = df_wind['H_direction']
    res['V_direction'] = df_wind['V_direction']
    res['U_axis'] = df_wind['U_axis']
    res['V_axis'] = df_wind['V_axis']
    res['W_axis'] = df_wind['W_axis']

    res['Index_2'] = df_wind.index.values

    res = res[["Index", "Index_2", "Date_Time", "Wind_Speed", "Wind_Speed_2D", "H_direction", "V_direction", "U_axis", "V_axis", "W_axis"]]
    
    #set index
    #res.index = pd.date_range(res.Index_2[0], res.Index_2.iloc[-1], freq="25L")
    
    #save file
    res.to_csv(f'{file_name}_1.csv', index=False)


DataEditor(file_name='raspberry/data/wind_data/12-09-23--22-02')
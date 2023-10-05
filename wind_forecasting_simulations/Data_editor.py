import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

freq = 10
num = int(40/freq)
set_New_freq = 25*num

#read data
df_wind = pd.read_csv('raspberry/anemometer/wind_data/25-09-23--16-49.csv')

#set index
df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="25L")

# Calculating mean
res = df_wind.groupby(np.arange(len(df_wind))//num, as_index=False).mean().round(4)

df_wind_2 = df_wind[::num]

res['Index'] = df_wind_2.Index.values

res['Index_2'] = df_wind_2.Index_2.values

res['Date_Time'] = df_wind_2.Date_Time.values

res = res[["Index", "Index_2", "Date_Time", "Wind_Speed", "Wind_Speed_2D", "H_direction", "V_direction", "U_axis", "V_axis", "W_axis"]]

#set index
res.index = pd.date_range(res.Index_2[0], res.Index_2.iloc[-1], freq=f'{str(set_New_freq)}L')

#save file
res.to_csv(f'raspberry/anemometer/wind_data/25-09-23--16-49_{str(freq)}Hz.csv', index=False)

plt.figure(figsize=(10,4))
plt.plot(df_wind.Wind_Speed)
plt.plot(res.Wind_Speed)
plt.title('Wind speed over Time', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

plt.show() 
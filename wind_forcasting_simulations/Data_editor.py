import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

#read data
df_wind = pd.read_csv('Wind_Data/measured_wind_2.csv')

#set index
df_wind.index = pd.date_range("18:35:00", "18:49:58.225000", freq="25L")

# Calculating mean
res = df_wind.groupby(np.arange(len(df_wind))//20, as_index=False).mean().round(4)

df_wind_2 = df_wind[::20]

res['Index'] = df_wind_2.Index.values

res['index_2'] = df_wind_2.index_2.values

res['date_time'] = df_wind_2.date_time.values

res = res[["Index", "index_2", "date_time", "Wind_Speed", "wind_speed_2D", "H_direction", "V_direction", "U_axis", "V_axis", "W_axis"]]

#set index
res.index = pd.date_range("18:35:00", "18:49:58.200000", freq="500L")

#save file
res.to_csv("Wind_Data/measured_wind_2_2Hz.csv", index=False)

plt.figure(figsize=(10,4))
plt.plot(df_wind.Wind_Speed)
plt.plot(res.Wind_Speed)
plt.title('Wind speed over Time', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

plt.show() 
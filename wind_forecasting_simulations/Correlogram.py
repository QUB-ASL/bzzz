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
df_wind = pd.read_csv('raspberry/anemometer/wind_data/25-09-23--16-49/25-09-23--16-49.csv')
df_wind_2 = pd.read_csv('raspberry/anemometer/wind_data/25-09-23--16-49/25-09-23--16-49_N_5.csv')
df_wind_3 = pd.read_csv('raspberry/anemometer/wind_data/25-09-23--16-49/25-09-23--16-49_N_10.csv')

#set index
df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="25L")
df_wind_2.index = pd.date_range(df_wind_2.Index_2[0], df_wind_2.Index_2.iloc[-1], freq="25L")
df_wind_3.index = pd.date_range(df_wind_3.Index_2[0], df_wind_3.Index_2.iloc[-1], freq="25L")


# ### DF_WIND_1 ###

# windspeed = pd.Series()
# windspeed_minus_1 = pd.Series()
# windspeed_U = pd.Series()
# windspeed_U_minus_1 = pd.Series()
# windspeed_V = pd.Series()
# windspeed_V_minus_1 = pd.Series()
# windspeed_W = pd.Series()
# windspeed_W_minus_1 = pd.Series()

# for x in range(10):
#     for t in range(2000):
#         windspeed[df_wind.index[t]] = df_wind.Wind_Speed[t]
#         windspeed_minus_1[df_wind.index[t]] = df_wind.Wind_Speed[t-x]
    
#     plt.figure(figsize=(10,4))
#     plt.scatter(windspeed, windspeed_minus_1)
#     plt.title(f'W_t against W_t-{str(x)}', fontsize=20)
#     plt.xlabel(f'W_t-{str(x)}', fontsize=16)
#     plt.ylabel('W_t', fontsize=16)

# for x in range(10):
#     for t in range(2000):
#         windspeed_U[df_wind.index[t]] = df_wind.U_axis[t]
#         windspeed_U_minus_1[df_wind.index[t]] = df_wind.U_axis[t-x]
    
#     plt.figure(figsize=(10,4))
#     plt.scatter(windspeed_U, windspeed_U_minus_1)
#     plt.title(f'U_t against U_t-{str(x)}', fontsize=20)
#     plt.xlabel(f'U_t-{str(x)}', fontsize=16)
#     plt.ylabel('U_t', fontsize=16)

# for x in range(10):
#     for t in range(2000):
#         windspeed_V[df_wind.index[t]] = df_wind.V_axis[t]
#         windspeed_V_minus_1[df_wind.index[t]] = df_wind.V_axis[t-x]
    
#     plt.figure(figsize=(10,4))
#     plt.scatter(windspeed_V, windspeed_V_minus_1)
#     plt.title(f'V_t against V_t-{str(x)}', fontsize=20)
#     plt.xlabel(f'V_t-{str(x)}', fontsize=16)
#     plt.ylabel('V_t', fontsize=16)

# for x in range(10):
#     for t in range(2000):
#         windspeed_W[df_wind.index[t]] = df_wind.W_axis[t]
#         windspeed_W_minus_1[df_wind.index[t]] = df_wind.W_axis[t-x]
    
#     plt.figure(figsize=(10,4))
#     plt.scatter(windspeed_W, windspeed_W_minus_1)
#     plt.title(f'W_t against W_t-{str(x)}', fontsize=20)
#     plt.xlabel(f'W_t-{str(x)}', fontsize=16)
#     plt.ylabel('W_t', fontsize=16)
    

# ### DF_WIND_2 ###

# windspeed_2 = pd.Series()
# windspeed_2_minus_1 = pd.Series()
# windspeed_2_U = pd.Series()
# windspeed_2_U_minus_1 = pd.Series()
# windspeed_2_V = pd.Series()
# windspeed_2_V_minus_1 = pd.Series()
# windspeed_2_W = pd.Series()
# windspeed_2_W_minus_1 = pd.Series()

# for x in range(10):
#     for t in range(2000):
#         windspeed_2[df_wind_2.index[t]] = df_wind_2.Wind_Speed[t]
#         windspeed_2_minus_1[df_wind_2.index[t]] = df_wind_2.Wind_Speed[t-x]
    
#     plt.figure(figsize=(10,4))
#     plt.scatter(windspeed_2, windspeed_2_minus_1)
#     plt.title(f'W_t against W_t-{str(x)}', fontsize=20)
#     plt.xlabel(f'W_t-{str(x)}', fontsize=16)
#     plt.ylabel('W_t', fontsize=16)

# for x in range(10):
#     for t in range(2000):
#         windspeed_2_U[df_wind_2.index[t]] = df_wind_2.U_axis[t]
#         windspeed_2_U_minus_1[df_wind_2.index[t]] = df_wind_2.U_axis[t-x]
    
#     plt.figure(figsize=(10,4))
#     plt.scatter(windspeed_2_U, windspeed_2_U_minus_1)
#     plt.title(f'U_t against U_t-{str(x)}', fontsize=20)
#     plt.xlabel(f'U_t-{str(x)}', fontsize=16)
#     plt.ylabel('U_t', fontsize=16)

# for x in range(10):
#     for t in range(2000):
#         windspeed_2_V[df_wind_2.index[t]] = df_wind_2.V_axis[t]
#         windspeed_2_V_minus_1[df_wind_2.index[t]] = df_wind_2.V_axis[t-x]
    
#     plt.figure(figsize=(10,4))
#     plt.scatter(windspeed_2_V, windspeed_2_V_minus_1)
#     plt.title(f'V_t against V_t-{str(x)}', fontsize=20)
#     plt.xlabel(f'V_t-{str(x)}', fontsize=16)
#     plt.ylabel('V_t', fontsize=16)

# for x in range(10):
#     for t in range(2000):
#         windspeed_2_W[df_wind_2.index[t]] = df_wind_2.W_axis[t]
#         windspeed_2_W_minus_1[df_wind_2.index[t]] = df_wind_2.W_axis[t-x]
    
#     plt.figure(figsize=(10,4))
#     plt.scatter(windspeed_2_W, windspeed_2_W_minus_1)
#     plt.title(f'W_t against W_t-{str(x)}', fontsize=20)
#     plt.xlabel(f'W_t-{str(x)}', fontsize=16)
#     plt.ylabel('W_t', fontsize=16)


# ### DF_WIND_3 ###

# windspeed_3 = pd.Series()
# windspeed_3_minus_1 = pd.Series()
# windspeed_3_U = pd.Series()
# windspeed_3_U_minus_1 = pd.Series()
# windspeed_3_V = pd.Series()
# windspeed_3_V_minus_1 = pd.Series()
# windspeed_3_W = pd.Series()
# windspeed_3_W_minus_1 = pd.Series()

# for x in range(10):
#     for t in range(2000):
#         windspeed_3[df_wind_3.index[t]] = df_wind_3.Wind_Speed[t]
#         windspeed_3_minus_1[df_wind_3.index[t]] = df_wind_3.Wind_Speed[t-x]
    
#     plt.figure(figsize=(10,4))
#     plt.scatter(windspeed_3, windspeed_3_minus_1)
#     plt.title(f'W_t against W_t-{str(x)}', fontsize=20)
#     plt.xlabel(f'W_t-{str(x)}', fontsize=16)
#     plt.ylabel('W_t', fontsize=16)

# for x in range(10):
#     for t in range(2000):
#         windspeed_3_U[df_wind_3.index[t]] = df_wind_3.U_axis[t]
#         windspeed_3_U_minus_1[df_wind_3.index[t]] = df_wind_3.U_axis[t-x]
    
#     plt.figure(figsize=(10,4))
#     plt.scatter(windspeed_3_U, windspeed_3_U_minus_1)
#     plt.title(f'U_t against U_t-{str(x)}', fontsize=20)
#     plt.xlabel(f'U_t-{str(x)}', fontsize=16)
#     plt.ylabel('U_t', fontsize=16)

# for x in range(10):
#     for t in range(2000):
#         windspeed_3_V[df_wind_3.index[t]] = df_wind_3.V_axis[t]
#         windspeed_3_V_minus_1[df_wind_3.index[t]] = df_wind_3.V_axis[t-x]
    
#     plt.figure(figsize=(10,4))
#     plt.scatter(windspeed_3_V, windspeed_3_V_minus_1)
#     plt.title(f'V_t against V_t-{str(x)}', fontsize=20)
#     plt.xlabel(f'V_t-{str(x)}', fontsize=16)
#     plt.ylabel('V_t', fontsize=16)

# for x in range(10):
#     for t in range(2000):
#         windspeed_3_W[df_wind_3.index[t]] = df_wind_3.W_axis[t]
#         windspeed_3_W_minus_1[df_wind_3.index[t]] = df_wind_3.W_axis[t-x]
    
#     plt.figure(figsize=(10,4))
#     plt.scatter(windspeed_3_W, windspeed_3_W_minus_1)
#     plt.title(f'W_t against W_t-{str(x)}', fontsize=20)
#     plt.xlabel(f'W_t-{str(x)}', fontsize=16)
#     plt.ylabel('W_t', fontsize=16)

### X AGAINST Y ###

windspeed_U = pd.Series()
windspeed_V = pd.Series()


for x in range(1):
    for t in range(2000):
        windspeed_U[df_wind_3.index[t]] = df_wind_3.U_axis[t]
        windspeed_V[df_wind_3.index[t]] = df_wind_3.H_direction[t]
    
    plt.figure(figsize=(10,4))
    plt.scatter(windspeed_U, windspeed_V)
    plt.title(f'U_t against V_t-{str(x)}', fontsize=20)
    plt.xlabel(f'V_t-{str(x)}', fontsize=16)
    plt.ylabel('U_t', fontsize=16)

plt.show()
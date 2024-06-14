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


y_10 = np.array([1.007,1.053,1.11,1.179,1.276,1.32,1.356,1.394,1.419,1.402,1.386])
# ,1.402,1.386,1.357,1.327,1.279,1.168,1.1,1.047,0.981,0.943,0.943,0.886,0.865,0.835,0.825,0.822,0.855,0.892,0.917,0.94,0.951,1.011
all_forecast = np.array([1.007,1.053,1.11,1.179,1.276,1.32,1.356,1.394,1.419])
error_1 = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0])
error_2 = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0])
error_3 = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0])
error_4 = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0])
error_5 = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0])

for x in range(100):

    y = np.array([df_wind.Wind_Speed[x],
                  df_wind.Wind_Speed[x + 1],
                  df_wind.Wind_Speed[x + 2],
                  df_wind.Wind_Speed[x + 3],
                  df_wind.Wind_Speed[x + 4],
                  df_wind.Wind_Speed[x + 5],
                  df_wind.Wind_Speed[x + 6],
                  df_wind.Wind_Speed[x + 7],
                  df_wind.Wind_Speed[x + 8]])
    
    # error = np.array([df_wind.Wind_Speed[x + 1] - y_10[-8],
    #                   df_wind.Wind_Speed[x + 2] - y_10[-7],
    #                   df_wind.Wind_Speed[x + 3] - y_10[-6],
    #                   df_wind.Wind_Speed[x + 4] - y_10[-5],
    #                   df_wind.Wind_Speed[x + 5] - y_10[-4],
    #                   df_wind.Wind_Speed[x + 6] - y_10[-3],
    #                   df_wind.Wind_Speed[x + 7] - y_10[-2],
    #                   df_wind.Wind_Speed[x + 8] - y_10[-1]]) 

    error_1 = np.delete(error_1, [-1, -2, -3])
    # error_2 = np.delete(error_2, [-1, -2, -3])
    # error_3 = np.delete(error_3, [-1, -2, -3, -4 , -5])
    # error_4 = np.delete(error_4, [-1, -2, -3, -4 , -5])
    # error_5 = np.delete(error_5, [-1, -2, -3, -4 , -5])

    error_1 = np.append(error_1,(df_wind.Wind_Speed[x + 8] - all_forecast[-3])) 
    error_2 = np.append(error_2,(df_wind.Wind_Speed[x + 8] - all_forecast[-2])) 
    # error_3 = np.append(error_3,(df_wind.Wind_Speed[x + 8] - all_forecast[-3])) 
    # error_4 = np.append(error_4,(df_wind.Wind_Speed[x + 8] - all_forecast[-2])) 
    # error_5 = np.append(error_5,(df_wind.Wind_Speed[x + 8] - all_forecast[-1])) 

    # if x > 0:
    #     error_2 = df_wind.Wind_Speed[x + 7] - all_forecast[-4]
    #     print(f"df_wind.Wind_Speed[x + 7] = {df_wind.Wind_Speed[x + 7]}")
    #     print(f"all_forecast[-4] = {all_forecast[-4]}")
    #     print(f"error_2 = {error_2}")

    for z in range(3):
        if z == 0:
            ARMA = ar1*(y[-1]) + ar2*(y[-2]) + ar3*(y[-3]) + ar4*(y[-4]) + ar5*(y[-5]) + ma1*(error_1[-1]) + ma2*(error_1[-2]) + ma3*(error_1[-3]) + ma4*(error_1[-4]) + ma5*(error_1[-5]) + ma6*(error_1[-6])+ ma7*(error_1[-7]) + ma8*(error_1[-8])
        if z > 0:
            ARMA = ar1*(y[-1]) + ar2*(y[-2]) + ar3*(y[-3]) + ar4*(y[-4]) + ar5*(y[-5]) + ma1*(error_2[-1]) + ma2*(error_2[-2]) + ma3*(error_2[-3]) + ma4*(error_2[-4]) + ma5*(error_2[-5]) + ma6*(error_2[-6])+ ma7*(error_2[-7]) + ma8*(error_2[-8])
        y = np.append(y, ARMA)
        all_forecast = np.append(all_forecast, ARMA)
        error_1 = np.append(error_1,0)
        print(f"error_2 = {error_2}")

    y_10 = np.append(y_10, y[-1])
    # print(f"y = {y}")
    # print(f"error = {error}")
print(f"all_forecast = {all_forecast}")

forecast = {'forecast': y_10}

df = pd.DataFrame(forecast)
df.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2[110], freq="25L")
df['real_wind'] = df_wind.Wind_Speed.values[0:111]
df['residuals'] = df.real_wind - df.forecast
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




# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from datetime import datetime
# from datetime import timedelta
# from time import time
# import matplotlib.dates as mdates
# import csv


# ## Read data
# df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--16-49/25-09-23--16-49_N_10.csv')

# ## Set index
# df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="25L")

# ## Plot Wind Speed against time
# plt.figure(figsize=(10,4))
# plt.plot(df_wind.Wind_Speed)
# plt.title('combined Wind speed over Time', fontsize=20)
# plt.ylabel('Wind Speed m/s', fontsize=16)

# ar1 = 1.572654
# ar2 = -1.193433
# ar3 = 0.9085445
# ar4 = -0.5089323
# ar5 = 0.2081693
# ma1 = -0.0713252
# ma2 = 0.9297537
# ma3 = 0.0202807
# ma4 = 0.8987153
# ma5 = -0.0014764
# ma6 = 0.9206075
# ma7 = 0.0372892
# ma8 = 0.8512221

# y = np.array([1.007,1.053,1.11,1.179,1.276,1.32,1.356,1.394,1.419])
# b1_list = np.array([0,0,0,0,0,0,0,0,0])
# b2_list = np.array([0,0,0,0,0,0,0,0,0])
# a1_list = np.array([0,0,0,0,0,0,0,0,0])
# a2_list = np.array([0,0,0,0,0,0,0,0,0])

# for x in range(1000):
#     a1 = df_wind.Wind_Speed[x + 8]
#     a2 = df_wind.Wind_Speed[x + 7]
#     a3 = df_wind.Wind_Speed[x + 6]
#     a4 = df_wind.Wind_Speed[x + 5]
#     a5 = df_wind.Wind_Speed[x + 4]
    
#     b1 = df_wind.Wind_Speed[x + 8] - y[-1] 
#     b2 = df_wind.Wind_Speed[x + 7] - y[-2] 
#     b3 = df_wind.Wind_Speed[x + 6] - y[-3] 
#     b4 = df_wind.Wind_Speed[x + 5] - y[-4] 
#     b5 = df_wind.Wind_Speed[x + 4] - y[-5] 
#     b6 = df_wind.Wind_Speed[x + 3] - y[-6] 
#     b7 = df_wind.Wind_Speed[x + 2] - y[-7] 
#     b8 = df_wind.Wind_Speed[x + 1] - y[-8] 

#     y = np.append(y, ar1*a1 + ar2*a2 + ar3*a3 + ar4*a4 + ar5*a5 + ma1*b1 + ma2*b2 + ma3*b3 + ma4*b4 + ma5*b5 + ma6*b6 + ma7*b7 + ma8*b8)

#     b1_list = np.append(b1_list, b1)
#     b2_list = np.append(b2_list, b2)
#     a1_list = np.append(a1_list, a1)
#     a2_list = np.append(a2_list, a2)

#     # y_10 = y[x+10]
#     # y_10 = np.append(y_10, y_10)

# forecast = {'forecast': y}

# df = pd.DataFrame(forecast)
# df['b1'] = b1_list
# df['b2'] = b2_list
# df.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2[1008], freq="25L")
# df['real_wind'] = df_wind.Wind_Speed.values[0:1009]
# df['a1'] = a1_list
# df['a2'] = a2_list
# df['residuals'] = df.real_wind - df.forecast
# df.to_csv("data.csv")

# ## Plot Residuals against time
# plt.figure(figsize=(10,4))
# plt.plot(df.residuals)
# plt.title('Residuals from ARIMA Model', fontsize=20)
# plt.ylabel('Residual', fontsize=16)
# plt.axhline(0, color='r', linestyle='--', alpha=0.2)

# ## Plot predictions and test data against time
# plt.figure(figsize=(10,4))
# plt.plot(df_wind.Wind_Speed)
# plt.plot(df.forecast)
# plt.legend(('Data', 'Predictions'), fontsize=16)
# plt.title('Wind Prediction', fontsize=20)
# plt.ylabel('Wind Speed', fontsize=16)

# plt.show()
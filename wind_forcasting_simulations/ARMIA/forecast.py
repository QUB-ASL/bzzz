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
df_wind = pd.read_csv('Wind_Data/measured_wind_2_1Hz.csv')

#set index
df_wind.index = pd.date_range("18:35:00", "18:49:58", freq="1000L")

plt.figure(figsize=(10,4))
plt.plot(df_wind.Wind_Speed)
plt.title('Wind speed over Time', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

acf_plot = plot_acf(df_wind.Wind_Speed, lags=50)
pacf_plot = plot_pacf(df_wind.Wind_Speed, lags=50)

train_end = 600
test_end = 690

train_data = df_wind.Wind_Speed[:train_end]
test_data = df_wind.Wind_Speed[(train_end):test_end]

# define model
model_1 = ARIMA(train_data, order=(3, 0, 8))
# model_2 = ARIMA(train_data, order=(6, 0, 0))

#fit the model
model_fit_1 = model_1.fit()
# model_fit_2 = model_2.fit()

# #summary of the model
# print(model_fit_1.summary())
# print(model_fit_1.params)

#get the predictions and residuals
predictions_1 = model_fit_1.predict(start=(train_end + 1),end=test_end)
# predictions_2 = model_fit_2.predict(start=(train_end + 1),end=test_end)
residuals_1 = test_data - predictions_1
# residuals_2 = test_data - predictions_2

start = time()
rolling_predictions_1 = pd.Series()
t_minus_x = pd.Series()
# rolling_predictions_2 = pd.Series()
for x in range(train_end, test_end):
    t_minus_x[df_wind.index[x+1]] = df_wind.Wind_Speed[x]
    updated_data = df_wind.Wind_Speed[x:x+1]
    model_fit_1 = model_fit_1.append(updated_data, refit=False)
    # model_fit_2 = model_fit_2.append(updated_data, refit=False)

    rolling_predictions_1[df_wind.index[x+1]] = model_fit_1.predict(x+1)
    # rolling_predictions_2[df_wind.index[x+10]] = model_fit_2.predict(x+10)

end = time()
print('Model Fitting Time:', end - start)

residuals_1_2 = test_data - rolling_predictions_1
# residuals_2_2 = test_data - rolling_predictions_2
residuals_t_minus_x = test_data - t_minus_x

plt.figure(figsize=(10,4))
plt.plot(residuals_1)
# plt.plot(residuals_2)
plt.legend(('residuals_1'), fontsize=16)
plt.title('Residuals from ARIMA Model', fontsize=20)
plt.ylabel('Error', fontsize=16)
plt.axhline(0, color='r', linestyle='--', alpha=0.2)

plt.figure(figsize=(10,4))
plt.plot(test_data)
plt.plot(predictions_1)
# plt.plot(predictions_2)
plt.legend(('Data', 'Predictions_1'), fontsize=16)
plt.title('Wind Prediction', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

plt.figure(figsize=(10,4))
plt.plot(test_data)
plt.plot(rolling_predictions_1)
# plt.plot(t_minus_x)
# plt.plot(rolling_predictions_2)
plt.legend(('Data', 'Predictions_1', 't_minus_x'), fontsize=16)
plt.title('Rolling Wind Prediction', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

plt.figure(figsize=(10,4))
plt.plot(residuals_1_2)
plt.plot(residuals_t_minus_x)
plt.legend(('residuals_1', 'residuals_t_minus_x'), fontsize=16)
plt.title('Residuals from rolling Wind Prediction', fontsize=20)
plt.ylabel('Error', fontsize=16)
plt.axhline(0, color='r', linestyle='--', alpha=0.2)

# plt.figure(figsize=(10,4))
# plt.plot(residuals_3)
# plt.title('Residuals from rolling Wind Prediction', fontsize=20)
# plt.ylabel('Error', fontsize=16)
# plt.axhline(0, color='r', linestyle='--', alpha=0.2)


# ####FIRST DIFFERENCE####
# #take first difference
# first_diffs = df_wind.Wind_Speed.values[1:] - df_wind.Wind_Speed.values[:-1]
# first_diffs = np.concatenate([first_diffs, [0]])

# #set first difference as variable in dataframe
# df_wind['FirstDifference'] = first_diffs
# print(df_wind.FirstDifference)

# plt.figure(figsize=(10,4))
# plt.plot(df_wind.FirstDifference)
# plt.title('First Difference over Time', fontsize=20)
# plt.ylabel('Wind Speed Difference', fontsize=16)

# first_diffs_acf_plot = plot_acf(df_wind.FirstDifference)
# first_diffs_pacf_plot = plot_pacf(df_wind.FirstDifference)

# first_diffs_train_data = df_wind.FirstDifference[1:train_end]
# first_diffs_test_data = df_wind.FirstDifference[(train_end):test_end]
# print(first_diffs_test_data)

# # define model
# first_diffs_model = ARIMA(first_diffs_train_data, order=(2, 1, 1))

# #fit the model
# first_diffs_model_fit = first_diffs_model.fit()

# #get the predictions and residuals
# first_diffs_predictions = first_diffs_model_fit.predict(start=(train_end + 1),end=test_end)
# first_diffs_residuals = first_diffs_test_data - first_diffs_predictions

# first_diffs_start = time()
# first_diffs_rolling_predictions = pd.Series()
# # first_diffs_rolling_predictions_2 = pd.Series()
# for x in range(train_end, test_end):
#     first_diffs_updated_data = df_wind.FirstDifference[x:x+1]
#     first_diffs_model_fit = first_diffs_model_fit.append(first_diffs_updated_data, refit=False)

#     first_diffs_rolling_predictions[df_wind.index[x+1]] = first_diffs_model_fit.predict(x+1)
#     # first_diffs_rolling_predictions_2[df_wind.index[x]] = first_diffs_model_fit.predict(x+40)
#     print(first_diffs_updated_data)

# first_diffs_end = time()
# print('Diffs Model Fitting Time:', first_diffs_end - first_diffs_start)

# first_diffs_residuals_2 = first_diffs_test_data - first_diffs_rolling_predictions
# # first_diffs_residuals_3 = first_diffs_test_data - first_diffs_rolling_predictions_2

# plt.figure(figsize=(10,4))
# plt.plot(first_diffs_residuals)
# plt.title('Residuals from First Difference ARIMA Model', fontsize=20)
# plt.ylabel('Error', fontsize=16)
# plt.axhline(0, color='r', linestyle='--', alpha=0.2)

# plt.figure(figsize=(10,4))
# plt.plot(first_diffs_test_data)
# plt.plot(first_diffs_predictions)
# plt.legend(('Data', 'Predictions'), fontsize=16)
# plt.title('Prediction for First Difference of Wind Speed', fontsize=20)
# plt.ylabel('Wind Speed', fontsize=16)

# plt.figure(figsize=(10,4))
# plt.plot(first_diffs_test_data)
# plt.plot(first_diffs_rolling_predictions)
# # plt.plot(rolling_predictions_2)
# plt.legend(('Data', 'Predictions_1', 'Predictions_2'), fontsize=16)
# plt.title('Rolling Wind Prediction', fontsize=20)
# plt.ylabel('Wind Speed', fontsize=16)

# plt.figure(figsize=(10,4))
# plt.plot(first_diffs_residuals_2)
# # plt.plot(residuals_2_2)
# plt.legend(('residuals_1', 'residuals_2'), fontsize=16)
# plt.title('Residuals from rolling Wind Prediction', fontsize=20)
# plt.ylabel('Error', fontsize=16)
# plt.axhline(0, color='r', linestyle='--', alpha=0.2)

# ####SECOND DIFFERENCE####
# #take second difference
# second_diffs = df_wind.FirstDifference.values[1:] - df_wind.FirstDifference.values[:-1]
# second_diffs = np.concatenate([second_diffs, [0]])

# #set second difference as variable in dataframe
# df_wind['SecondDifference'] = second_diffs

# plt.figure(figsize=(10,4))
# plt.plot(df_wind.SecondDifference)
# plt.title('Second Difference over Time', fontsize=20)
# plt.ylabel('Wind Speed Second Difference', fontsize=16)

# acf_plot = plot_acf(df_wind.SecondDifference)
# pacf_plot = plot_pacf(df_wind.SecondDifference)

# second_diffs_train_data = df_wind.SecondDifference[1:train_end]
# second_diffs_test_data = df_wind.SecondDifference[(train_end):test_end]

# # define model
# second_diffs_model = ARIMA(second_diffs_train_data, order=(11, 2, 1))

# #fit the model
# second_diffs_start = time()
# second_diffs_model_fit = second_diffs_model.fit()
# second_diffs_end = time()
# print('Model Fitting Time:', second_diffs_end - second_diffs_start)

# #summary of the model
# #print(model_fit.summary())

# #get the predictions and residuals
# second_diffs_predictions = second_diffs_model_fit.predict(start=(train_end + 1),end=test_end)
# second_diffs_residuals = second_diffs_test_data - second_diffs_predictions

# plt.figure(figsize=(10,4))
# plt.plot(second_diffs_residuals)
# plt.title('Residuals from ARIMA Model', fontsize=20)
# plt.ylabel('Error', fontsize=16)
# plt.axhline(0, color='r', linestyle='--', alpha=0.2)
 
# plt.figure(figsize=(10,4))
# plt.plot(second_diffs_test_data)
# plt.plot(second_diffs_predictions)
# plt.legend(('Data', 'Predictions'), fontsize=16)
# plt.title('Prediction for Second Difference of Wind Speed', fontsize=20)
# plt.ylabel('Wind Speed', fontsize=16)

plt.show()
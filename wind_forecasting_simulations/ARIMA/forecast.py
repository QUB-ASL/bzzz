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

## Read data
df_wind = pd.read_csv('raspberry/anemometer/wind_data/25-09-23--16-49/25-09-23--16-49_N_10.csv')

## Set index
df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="25L")

## Plot Wind Speed against time
plt.figure(figsize=(10,4))
plt.plot(df_wind.U_axis)
plt.title('Wind speed over Time', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

## Plot ACF and PACF
acf_plot = plot_acf(df_wind.U_axis, lags=50)
pacf_plot = plot_pacf(df_wind.U_axis, lags=50)

## set where to split the data
train_end = 35000
test_end = 35500

## Split the data 
train_data = df_wind.U_axis[:train_end]
test_data = df_wind.U_axis[(train_end):test_end]

## Define model
model_1 = ARIMA(train_data, order=(6, 0, 0))
# model_2 = ARIMA(train_data, order=(6, 0, 0))

## Fit the model
model_fit_1 = model_1.fit()
# model_fit_2 = model_2.fit()

# ## Summary of the model
# print(model_fit_1.summary())
# print(model_fit_1.params)

## Get the 'Long' predictions and residuals
predictions_1 = model_fit_1.predict(start=(train_end + 1),end=test_end)
# predictions_2 = model_fit_2.predict(start=(train_end + 1),end=test_end)
residuals_1 = test_data - predictions_1
# residuals_2 = test_data - predictions_2

 
start = time()
## Define series 
rolling_predictions_1 = pd.Series()
t_minus_x = pd.Series()
# rolling_predictions_2 = pd.Series()

## Set prediction horizon length 
prediction_horizon_1 = 5
# prediction_horizon_2 = 10

## Rolling prediction for wind speed
for x in range(train_end, test_end):
    t_minus_x[df_wind.index[x+10]] = df_wind.U_axis[x]
    updated_data = df_wind.U_axis[x:x+1]
    model_fit_1 = model_fit_1.append(updated_data, refit=False)
    # model_fit_2 = model_fit_2.append(updated_data, refit=False)

    rolling_predictions_1[df_wind.index[x+prediction_horizon_1]] = model_fit_1.predict(x+prediction_horizon_1)
    # rolling_predictions_2[df_wind.index[x+prediction_horizon_2]] = model_fit_2.predict(x+prediction_horizon_2)

end = time()
print('Model Fitting Time:', end - start)

## Get residuals for rolling prediction and using previous wind speed
residuals_rolling_predictions_1 = test_data - rolling_predictions_1
# residuals_rolling_predictions_2 = test_data - rolling_predictions_2
residuals_t_minus_x = test_data - t_minus_x

## Plot Residuals against time for 'long' prediction
plt.figure(figsize=(10,4))
plt.plot(residuals_1)
# plt.plot(residuals_2)
plt.legend(('residuals_1'), fontsize=16)
plt.title('Residuals from ARIMA Model', fontsize=20)
plt.ylabel('Error', fontsize=16)
plt.axhline(0, color='r', linestyle='--', alpha=0.2)

## Plot 'long' predictions and test data against time
plt.figure(figsize=(10,4))
plt.plot(test_data)
plt.plot(predictions_1)
# plt.plot(predictions_2)
plt.legend(('Data', 'Predictions_1'), fontsize=16)
plt.title('Wind Prediction', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

## Plot rolling predictions and test data against time
plt.figure(figsize=(10,4))
plt.plot(test_data)
plt.plot(rolling_predictions_1)
plt.plot(t_minus_x)
# plt.plot(rolling_predictions_2)
plt.legend(('Data', '10 step Predictions', 't_minus_x'), fontsize=16)
plt.title('Rolling Wind Prediction', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

## Plot Residuals against time for rolling prediction
plt.figure(figsize=(10,4))
plt.plot(residuals_rolling_predictions_1)
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
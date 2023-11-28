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
import seaborn as sns

## Read data
df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--16-49/25-09-23--16-49_N_10.csv')

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
test_end = 35100

## Split the data 
train_data = df_wind.U_axis[:train_end]
test_data = df_wind.U_axis[(train_end):test_end]

## Define models
model_1 = ARIMA(train_data, order=(6, 0, 6))
model_2 = ARIMA(train_data, order=(1, 0, 0))

## Fit the models
model_fit_1 = model_1.fit()
model_fit_2 = model_2.fit()

# ## Summary of the model
# print(model_fit_1.summary())
# print(model_fit_1.params)

## Get the 'Long' predictions and residuals
predictions_1 = model_fit_1.predict(start=(train_end + 1),end=test_end)
predictions_2 = model_fit_2.predict(start=(train_end + 1),end=test_end)
residuals_1 = test_data - predictions_1
residuals_2 = test_data - predictions_2

start = time()
## Define dictions and series
rolling_predictions_1 = {}
t_minus_x = pd.Series()
rolling_predictions_2 = {}
error_i_1 = pd.Series()
error_i_2 = pd.Series()

## Set prediction horizon length 
prediction_horizon_1 = 10
prediction_horizon_2 = 10

## multiple Rolling predictions and errors for wind speed
for x in range(train_end, test_end):
    t_minus_x[df_wind.index[x+1]] = df_wind.U_axis[x]
    updated_data = df_wind.U_axis[x:x+1]
    model_fit_1 = model_fit_1.append(updated_data, refit=False)
    model_fit_2 = model_fit_2.append(updated_data, refit=False)

    rolling_predictions_1[x+1] = model_fit_1.predict(start=(x+1),end=(x+prediction_horizon_1))
    rolling_predictions_2[x+1] = model_fit_2.predict(start=(x+1),end=(x+prediction_horizon_2))
    error_i_1[df_wind.index[x]] = np.sqrt(sum((df_wind.U_axis[x+1:(x+prediction_horizon_1+1)] 
                                               - rolling_predictions_1[x+1])**2)/prediction_horizon_1)
    error_i_2[df_wind.index[x]] = np.sqrt(sum((df_wind.U_axis[x+1:(x+prediction_horizon_2+1)] 
                                               - rolling_predictions_2[x+1])**2)/prediction_horizon_2)

end = time()

## Set quantile error 
alpha_level = 0.95
quantile_error_1 = np.quantile(error_i_1, alpha_level)
quantile_error_2 = np.quantile(error_i_2, alpha_level)

print('Model Fitting Time:', end - start)

# residuals_1_2 = test_data - rolling_predictions_1
# residuals_2_2 = test_data - rolling_predictions_2
residuals_t_minus_x = test_data - t_minus_x

## Plot Residuals against time for 'long' prediction
plt.figure(figsize=(10,4))
plt.plot(residuals_1)
plt.plot(residuals_2)
plt.legend(('residuals_1'), fontsize=16)
plt.title('Residuals from ARIMA Model', fontsize=20)
plt.ylabel('Error', fontsize=16)
plt.axhline(0, color='r', linestyle='--', alpha=0.2)

## Plot 'long' predictions and test data against time
plt.figure(figsize=(10,4))
plt.plot(test_data)
plt.plot(predictions_1)
plt.plot(predictions_2)
plt.legend(('Data', 'Predictions_1'), fontsize=16)
plt.title('Wind Prediction', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

## Plot rolling predictions 1 and test data against time
plt.figure(figsize=(10,4))
plt.plot(test_data)
for x in range(train_end+1, test_end):
    plt.plot(rolling_predictions_1[x])
plt.title('Rolling Wind Prediction', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

## Plot rolling predictions 2 and test data against time
plt.figure(figsize=(10,4))
plt.plot(test_data)
for x in range(train_end+1, test_end):
    plt.plot(rolling_predictions_2[x])
plt.title('Rolling Wind Prediction', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

## Plot RMSE 
plt.figure(figsize=(10,4))
sns.distplot(error_i_1, hist=False)
sns.distplot(error_i_2, hist=False)
plt.plot([quantile_error_1, quantile_error_1], [0, 1], color='C0')
plt.plot([quantile_error_2, quantile_error_2], [0, 1], color='C1')
plt.legend(('Error_1', 'Error_2'), fontsize=16)
plt.title('Error Index', fontsize=20)
plt.ylabel('Density', fontsize=16)
plt.xlabel('Error value', fontsize=16)

plt.show()
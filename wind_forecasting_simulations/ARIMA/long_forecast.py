import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from pandas.plotting import register_matplotlib_converters
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
register_matplotlib_converters()
from time import time

## Read Data
df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--16-49_1Hz.csv')

## Set Index
df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="1000L")

## Plot Wind Speed against time
plt.figure(figsize=(10,4))
plt.plot(df_wind.Wind_Speed)
plt.title('Wind speed over Time', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

## Plot ACF and PACF
acf_plot = plot_acf(df_wind.Wind_Speed, lags=50)
pacf_plot = plot_pacf(df_wind.Wind_Speed)

## Set where to split the data 
train_end = 800
test_end = 1000

## Split the data 
train_data = df_wind.Wind_Speed[1:train_end]
test_data = df_wind.Wind_Speed[(train_end):test_end]

## Define model
model = ARIMA(train_data, order=(4, 0, 20))

## Fit the model
start = time()
model_fit = model.fit()
end = time()
print('Model Fitting Time:', end - start)

# ## Summary of the model
# print(model_fit.summary())

## Get the predictions and residuals
predictions = model_fit.predict(start=(train_end + 1),end=test_end)
residuals = test_data - predictions

## Plot Residuals against time
plt.figure(figsize=(10,4))
plt.plot(residuals)
plt.title('Residuals from ARIMA Model', fontsize=20)
plt.ylabel('Residual', fontsize=16)
plt.axhline(0, color='r', linestyle='--', alpha=0.2)

## Plot predictions and test data against time
plt.figure(figsize=(10,4))
plt.plot(test_data)
plt.plot(predictions)
plt.legend(('Data', 'Predictions'), fontsize=16)
plt.title('Wind Prediction', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)


####FIRST DIFFERENCE####
## Take first difference
first_diffs = df_wind.Wind_Speed.values[1:] - df_wind.Wind_Speed.values[:-1]
first_diffs = np.concatenate([first_diffs, [0]])

## Set first difference as variable in dataframe
df_wind['FirstDifference'] = first_diffs

## Plot first difference of Wind Speed against time
plt.figure(figsize=(10,4))
plt.plot(df_wind.FirstDifference)
plt.title('First Difference over Time', fontsize=20)
plt.ylabel('Wind Speed Difference', fontsize=16)

## Plot ACF and PACF of first difference of Wind Speed
acf_plot = plot_acf(df_wind.FirstDifference)
pacf_plot = plot_pacf(df_wind.FirstDifference)

## Split the data
first_diffs_train_data = df_wind.FirstDifference[1:train_end]
first_diffs_test_data = df_wind.FirstDifference[(train_end):test_end]

## Define model
first_diffs_model = ARIMA(first_diffs_train_data, order=(4, 1, 3))

## Fit the model
first_diffs_start = time()
first_diffs_model_fit = first_diffs_model.fit()
first_diffs_end = time()
print('Model Fitting Time:', first_diffs_end - first_diffs_start)

# ## Summary of the model
# print(first_diffs_model_fit.summary())

## Get the predictions and residuals
first_diffs_predictions = first_diffs_model_fit.predict(start=(train_end + 1),end=test_end)
first_diffs_residuals = first_diffs_test_data - first_diffs_predictions

## Plot Residuals against time for first difference of Wind Speed
plt.figure(figsize=(10,4))
plt.plot(first_diffs_residuals)
plt.title('Residuals from First Difference ARIMA Model', fontsize=20)
plt.ylabel('Residual', fontsize=16)
plt.axhline(0, color='r', linestyle='--', alpha=0.2)

## plot predictions and test data against time for first difference of Wind Speed
plt.figure(figsize=(10,4))
plt.plot(first_diffs_test_data)
plt.plot(first_diffs_predictions)
plt.legend(('Data', 'Predictions'), fontsize=16)
plt.title('Prediction for First Difference of Wind Speed', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)


####SECOND DIFFERENCE####
## Take second difference
second_diffs = df_wind.FirstDifference.values[1:] - df_wind.FirstDifference.values[:-1]
second_diffs = np.concatenate([second_diffs, [0]])

## Set second difference as variable in dataframe
df_wind['SecondDifference'] = second_diffs

## Plot second difference of Wind Speed against time
plt.figure(figsize=(10,4))
plt.plot(df_wind.SecondDifference)
plt.title('Second Difference over Time', fontsize=20)
plt.ylabel('Wind Speed Second Difference', fontsize=16)

## Plot ACF and PACF of second difference of Wind Speed
acf_plot = plot_acf(df_wind.SecondDifference)
pacf_plot = plot_pacf(df_wind.SecondDifference)

## Split the data
second_diffs_train_data = df_wind.SecondDifference[1:train_end]
second_diffs_test_data = df_wind.SecondDifference[(train_end):test_end]

## Define model
second_diffs_model = ARIMA(second_diffs_train_data, order=(11, 2, 1))

## Fit the model
second_diffs_start = time()
second_diffs_model_fit = second_diffs_model.fit()
second_diffs_end = time()
print('Model Fitting Time:', second_diffs_end - second_diffs_start)

# ## Summary of the model
# print(second_diffs_model_fit.summary())

## Get the predictions and residuals
second_diffs_predictions = second_diffs_model_fit.predict(start=(train_end + 1),end=test_end)
second_diffs_residuals = second_diffs_test_data - second_diffs_predictions

## plot Residuals against time for second difference of Wind Speed
plt.figure(figsize=(10,4))
plt.plot(second_diffs_residuals)
plt.title('Residuals from ARIMA Model', fontsize=20)
plt.ylabel('Error', fontsize=16)
plt.axhline(0, color='r', linestyle='--', alpha=0.2)

## plot predictions and test data against time for second difference of Wind Speed
plt.figure(figsize=(10,4))
plt.plot(second_diffs_test_data)
plt.plot(second_diffs_predictions)
plt.legend(('Data', 'Predictions'), fontsize=16)
plt.title('Prediction for Second Difference of Wind Speed', fontsize=20)
plt.ylabel('Wind Speed', fontsize=16)

plt.show()
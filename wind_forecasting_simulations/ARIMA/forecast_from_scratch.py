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

# y = np.array([1.394,1.356,1.32,1.276,1.179,1.11,1.053,1.007])
# y_hat = np.array([1.394,1.356,1.32,1.276,1.179,1.11,1.053,1.007])
# e = np.array([0.,0.,0.,0.,0.,0.,0.,0.])
# forecast_cache = np.array([1.007,1.053,1.11,1.179,1.276,1.32,1.356,1.394])
# t_plus_x_cache = np.array([1.007,1.053,1.11,1.179,1.276,1.32,1.356,1.394])

# for x in range(10):
#     forecast_cache = np.append(forecast_cache,df_wind.Wind_Speed[x+8])
#     t_plus_x_cache = np.append(t_plus_x_cache,df_wind.Wind_Speed[x+8])

# for x in range(1000):

#     y = np.roll(y,1)
#     y[0] = df_wind.Wind_Speed[x+8]

#     y_temp = y
#     e_temp = e 

#     ARMA = (ar1*(y[0]) + ar2*(y[1]) + ar3*(y[2]) + ar4*(y[3]) + ar5*(y[4]) 
#             + ma1*(e[0]) + ma2*(e[1]) + ma3*(e[2]) + ma4*(e[3]) 
#             + ma5*(e[4]) + ma6*(e[5]) + ma7*(e[6]) + ma8*(e[7]))
    
#     y_hat = np.roll(y_hat,1)
#     y_hat[0] = ARMA

#     for z in range(10):
#         ARMA2 = (ar1*(y_temp[0]) + ar2*(y_temp[1]) + ar3*(y_temp[2]) + ar4*(y_temp[3]) + ar5*(y_temp[4]) 
#             + ma1*(e_temp[0]) + ma2*(e_temp[1]) + ma3*(e_temp[2]) + ma4*(e_temp[3]) 
#             + ma5*(e_temp[4]) + ma6*(e_temp[5]) + ma7*(e_temp[6]) + ma8*(e_temp[7]))
#         # print(ARMA2)
#         y_temp = np.roll(y_temp,1)
#         y_temp[0] = ARMA2
#         e_temp = np.roll(e_temp,1)
#         e_temp[0] = 0

#     forecast_cache = np.append(forecast_cache,ARMA2)
#     e = y - y_hat
#     t_plus_x_cache = np.append(t_plus_x_cache,df_wind.Wind_Speed[x])

# forecast = {'forecast': forecast_cache}
# t_plus_x = {'t_plus_x': t_plus_x_cache}

# df = pd.DataFrame(forecast)
# df.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2[1017], freq="25L")
# df['real_wind'] = df_wind.Wind_Speed.values[0:1018]
# df['residuals'] = df.real_wind - df.forecast
# df['t_plus_x'] = t_plus_x_cache
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





############################################################################
###########################################################################







# import numpy as np
# from collections import deque
# import matplotlib.pyplot as plt

# class ARMAPredictor:
#     def __init__(self, ar_weights, ma_weights, window_size, prediction_horizon=10):
#         """
#         Initialize the ARMA predictor with manually set AR and MA weights.

#         :param ar_weights: List or array of AR (autoregressive) weights.
#         :param ma_weights: List or array of MA (moving average) weights.
#         :param window_size: Number of recent data points to store for predictions.
#         :param prediction_horizon: Number of steps ahead to predict.
#         """
#         self.ar_weights = np.array(ar_weights)
#         self.ma_weights = np.array(ma_weights)
#         self.window_size = window_size
#         self.prediction_horizon = prediction_horizon
        
#         self.data = deque(maxlen=window_size)  # Rolling window for recent data
#         self.errors = deque(maxlen=window_size)  # Rolling window for recent errors
#         self.all_data = []  # Store all actual data points for plotting
#         self.predicted_values = []  # Store predictions for plotting

#     def update_data(self, new_value):
#         """
#         Update the data with a new incoming data point and make predictions.

#         :param new_value: The latest observed data point.
#         """
#         # Add new data point to history and store it for plotting
#         self.data.append(new_value)
#         self.all_data.append(new_value)

#         # Generate predictions only if enough data is available
#         if len(self.data) >= max(len(self.ar_weights), len(self.ma_weights)):
#             temp_data = deque(self.data, maxlen=self.window_size)
#             temp_errors = deque(self.errors, maxlen=self.window_size)
            
#             # Store predictions for the specified prediction horizon
#             future_predictions = []
#             for step in range(self.prediction_horizon):
#                 # Calculate AR component
#                 ar_component = np.dot(self.ar_weights, list(temp_data)[-len(self.ar_weights):][::-1])

#                 # Calculate MA component only if there are enough error terms
#                 if len(temp_errors) >= len(self.ma_weights):
#                     ma_component = np.dot(self.ma_weights, list(temp_errors)[-len(self.ma_weights):][::-1])
#                 else:
#                     # Not enough errors; assume missing errors as zero
#                     ma_component = np.dot(self.ma_weights[:len(temp_errors)], list(temp_errors)[::-1])

#                 # Prediction is the sum of AR and MA components
#                 prediction = ar_component + ma_component
#                 future_predictions.append(prediction)

#                 # Update temporary data and errors for the next step
#                 temp_data.append(prediction)
#                 temp_errors.append(new_value - prediction)  # Update error based on actual vs predicted
            
#             # Append the last prediction of the future predictions to the predicted values
#             if len(self.predicted_values) < len(self.all_data) - self.prediction_horizon + 1:
#                 self.predicted_values.append(future_predictions[0])  # Store only the first prediction for plotting
#             else:
#                 self.predicted_values[-1] = future_predictions[0]  # Update the latest prediction

#         else:
#             # Not enough data to make a prediction
#             self.predicted_values.append(np.nan)
        
#         print(self.predicted_values)

#     def update_weights(self, ar_weights=None, ma_weights=None):
#         """
#         Update the AR and/or MA weights of the model.

#         :param ar_weights: New AR weights, if specified.
#         :param ma_weights: New MA weights, if specified.
#         """
#         if ar_weights is not None:
#             self.ar_weights = np.array(ar_weights)
#         if ma_weights is not None:
#             self.ma_weights = np.array(ma_weights)

#     def plot_predictions(self):
#         """
#         Plot the actual data points versus the predictions.
#         """
#         plt.figure(figsize=(12, 6))
#         plt.plot(self.all_data, label="Actual Data", color='blue')
#         plt.plot(self.predicted_values, label=f"{self.prediction_horizon} Step Ahead Prediction", color='orange', linestyle='--')
        
#         plt.xlabel("Time Steps")
#         plt.ylabel("Values")
#         plt.title("Actual Data vs. Predictions")
#         plt.legend()
#         plt.show()

# # Example usage:
# # Define initial AR and MA weights and the window size
# ar_weights = [1]  # Set AR weight to 1 for testing
# ma_weights = [2]   # MA weights for lag 1 and lag 2
# window_size = 20          # Size of the rolling window
# prediction_horizon = 1   # Number of steps to predict ahead

# # Instantiate the ARMAPredictor
# predictor = ARMAPredictor(ar_weights=ar_weights, ma_weights=ma_weights, window_size=window_size, prediction_horizon=prediction_horizon)

# # Simulate adding new data points and generating predictions
# new_data_points = [1.2, 0.9, 1.1, 1.0, 0.7, 1.3, 1.4, 1.0, 1.5, 1.2, 1.3, 0.8, 1.1, 1.3, 1.4, 1.6, 1.2, 1.1]  # Sample data points
# for new_point in new_data_points:
#     predictor.update_data(new_point)

# # Plot actual data vs. predictions
# predictor.plot_predictions()
























#############################################################################
#############################################################################









import pmdarima as pm
from collections import deque

# Initialize a deque to store recent smoothed wind speed data
historical_data = deque(maxlen=2400)  # Example: 1 minute of data at 40 Hz

# Fit initial ARIMA model with smoothed historical data
initial_model = pm.auto_arima(list(historical_data), seasonal=False)

# Real-time loop for forecasting and model updating
while True:
    new_observation = get_new_smoothed_wind_speed()  # Get latest smoothed wind speed at 40 Hz
    
    # Append new observation to historical data
    historical_data.append(new_observation)

    # Predict 10 steps ahead
    forecast = initial_model.predict(n_periods=10)

    # Update the model with the latest observation
    initial_model.update(new_observation)

    # Periodically re-fit the model with recent data if necessary
    if time_to_refit_model():  # Implement this based on desired frequency
        initial_model = pm.auto_arima(list(historical_data), seasonal=False)

    # Use or log the 10-step forecast as needed
    print("10-step forecast:", forecast)




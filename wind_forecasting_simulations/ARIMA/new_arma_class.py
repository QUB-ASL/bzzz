import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from time import time

class ARIMA:
    def __init__(self, prediction_horizon, p, d, q, fix_params=None):
        self.prediction_horizon = prediction_horizon
        self.p = p
        self.d = d
        self.q = q
        self.fix_params = fix_params
        self.model_fit = None

    def fit(self, train_data):
        self.model = SARIMAX(train_data, order=(self.p, self.d, self.q))
        self.model_fit = self.model.fit() if self.fix_params is None else self.model.fit(fix_params=self.fix_params)

    def predict(self, new_data_point):
        # Update model state directly using Kalman filtering without full re-fit
        self.model_fit = self.model_fit.extend(new_data_point)
        
        # Directly generate the next prediction
        prediction = self.model_fit.get_forecast(steps=self.prediction_horizon).predicted_mean[-1]
        return prediction

    def plot_predictions(self, train_data, test_data, predictions):
        plt.figure(figsize=(10, 6))
        plt.plot(train_data, label='Training Data')
        plt.plot(range(len(train_data), len(train_data) + len(test_data)), test_data, label='Test Data')
        plt.plot(range(len(train_data) + self.prediction_horizon, len(train_data) + len(predictions) + self.prediction_horizon,), predictions, label='Predictions')
        plt.legend()
        plt.show()

# Example usage
if __name__ == "__main__":
    # Read Data
    df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[3])
    train_data = df_wind.values[:10000]
    test_data = df_wind.values[10000:40000]

    # Initialize and fit the model
    model = ARIMA(prediction_horizon=10, p=5, d=0, q=8)
    model.fit(train_data)

    # Make predictions
    predictions = []
    start = time()
    for i in test_data:
        predictions.append(model.predict([i]))  # Predict using real-time sequential updates
    end = time()
    print('Model predicting Time:', end - start)

    # Plot the results
    model.plot_predictions(train_data, test_data, predictions)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import seaborn as sns
import keras
from sklearn.metrics import mean_squared_error

def to_sequences_lstm(dataset, seq_size=1, prediction_size=1):
    x, y = [], []
    for i in range(len(dataset) - seq_size - prediction_size):
        x_seq = dataset[i:i + seq_size]
        y_val = dataset[i + seq_size + prediction_size - 1]
        x.append(x_seq)
        y.append(y_val)
    return np.array(x), np.array(y)

max_wind_speed = 10

# Load and normalize data
df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[8])
dataset = df_wind.values.astype('float32')
dataset = (dataset + max_wind_speed) / (2 * max_wind_speed)

# Configuration
seq_size = 10
prediction_size = 40

# Create LSTM-compatible sequences
X, Y = to_sequences_lstm(dataset, seq_size, prediction_size)
X = X.reshape((X.shape[0], X.shape[1], 1))  # LSTM expects 3D input

# Load model
model = keras.saving.load_model("model_V_LSTM.keras")

# Predict
Predict = model.predict(X)
Predict = Predict.reshape(-1, 1)
Y = Y.reshape(1, -1)

# Unnormalize
dataset = dataset * 2 * max_wind_speed - max_wind_speed
Predict = Predict * 2 * max_wind_speed - max_wind_speed
Y = Y * 2 * max_wind_speed - max_wind_speed

# Print predictions
print(Y[0])
print(Predict[:, 0])

# Calculate RMSE
RMSE_Score = math.sqrt(mean_squared_error(Y[0], Predict[:, 0]))
print('Prediction Score: %f RMSE' % RMSE_Score)

errors = np.sqrt((Y[0] - Predict[:, 0]) ** 2)

# Save errors
df_error = pd.DataFrame(errors, columns=['Error'])
df_error.to_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_10_LSTM.csv', index=False)

quantile_error = np.quantile(errors, 0.95)
print(f'95% quantile error: {quantile_error}')

# Align predictions for plotting
PredictPlot = np.empty_like(dataset)
PredictPlot[:, :] = np.nan
PredictPlot[seq_size + prediction_size:, :] = Predict

# Plot original vs predicted
plt.figure(figsize=(10, 4))
plt.plot(dataset, label='Data')
plt.plot(PredictPlot, label='Prediction')
plt.legend(fontsize=12)
plt.title(f'LSTM Forecast using {prediction_size} steps (1 second)', fontsize=20)
plt.xlabel('Time step', fontsize=16)
plt.ylabel('Wind Speed (m/s)', fontsize=16)

# Plot prediction error
plt.figure(figsize=(10, 4))
plt.plot(dataset - PredictPlot)

# Plot error distribution
plt.figure(figsize=(10, 4))
sns.kdeplot(errors, color='blue')
plt.axvline(RMSE_Score, color='darkblue', linestyle='--')
plt.text(RMSE_Score, 0.5, f'RMSE: {RMSE_Score:.2f}', color='darkblue', fontsize=12, ha='center')
plt.axvline(quantile_error, color='red', linestyle='--')
plt.text(quantile_error, 0.4, f'95% Quantile\nError: {quantile_error:.2f}', color='red', fontsize=12, ha='center')
plt.title(f'Error Distribution of LSTM Forecast ({prediction_size} step horizon)', fontsize=20)
plt.ylabel('Probability Density', fontsize=16)
plt.xlabel('Error (m/s)', fontsize=16)

plt.show()

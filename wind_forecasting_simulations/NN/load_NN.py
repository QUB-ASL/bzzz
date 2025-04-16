
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import seaborn as sns
import keras
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

def to_sequences(dataset, seq_size=1):
    x = []
    y = []
    y_only_ph = []

    for i in range(len(dataset)-seq_size-prediction_size):
        window = dataset[(i+seq_size):i:-1, 0]
        x.append(window)
        y_outputs = dataset[(i+seq_size+1):(i+seq_size+prediction_size+1), 0]
        y.append(y_outputs)
        y_only_ph.append([y_outputs[-1]])
        
    return np.array(x),np.array(y_only_ph)

def get_last_prediction(data_set, prediction_size):
    output_array = []

    for i in range(len(data_set)):
        output = data_set[i][prediction_size-1]
        output_array.append(output)
    return np.array(output_array)

max_wind_speed = 10

## Read Data
df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[8])

dataset = df_wind.values
dataset = df_wind.values.astype('float32')

dataset = (dataset + max_wind_speed)/(2*max_wind_speed)

seq_size = 10
prediction_size = 10

X, Y = to_sequences(dataset, seq_size)

model = keras.saving.load_model("model_V.keras")

Predict = model.predict(X)
# Predict = get_last_prediction(Predict, prediction_size)
Predict = np.reshape(Predict, (-1, 1))

# Y = get_last_prediction(Y, prediction_size)
Y = np.reshape(Y, (1, -1))

dataset = dataset * 2 * max_wind_speed - max_wind_speed
Predict = Predict * 2 * max_wind_speed - max_wind_speed
Y = Y * 2 * max_wind_speed - max_wind_speed

# Predict_list = np.array([])
# for i in range(len(X)):
#     Predict = model.predict(np.array([X[i]]), verbose=0)
#     # Predict = get_last_prediction(Predict, prediction_size)
#     # if i > prediction_size:
#     #     last_error = Y[i] - Predict_list[-1]
#     #     Predict = Predict + 0.9*last_error
#     Predict_list = np.append(Predict_list, Predict)
#     Predict_list = np.reshape(Predict_list, (-1, 1))

# # Y = get_last_prediction(Y, prediction_size)
# Y = np.reshape(Y, (1, -1))

# dataset = dataset * 2 * max_wind_speed - max_wind_speed
# Predict = Predict_list * 2 * max_wind_speed - max_wind_speed
# Y = Y * 2 * max_wind_speed - max_wind_speed

print(Y[0])
print(Predict[:,0])

# calculate root mean squared error
RMSE_Score = math.sqrt(mean_squared_error(Y[0], Predict[:,0]))
print('Prediction Score: %f RMSE' % (RMSE_Score))

errors = np.sqrt((Y[0] - Predict[:,0])**2)

#save errors to csv file
df_error = pd.DataFrame(errors, columns=['Error'])
df_error.to_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_10_NN_1.csv', index=False)

quantile_error = np.quantile(errors, 0.95)
print(f'95% quantile error: {quantile_error}')


# shift predictions for plotting
#we must shift the predictions so that they align on the x-axis with the original dataset. 
PredictPlot = np.empty_like(dataset)
PredictPlot[:, :] = np.nan
PredictPlot[seq_size+prediction_size:, :] = Predict

# shift data for comparing plotting
dataset_t_plus_prediction_step = np.empty_like(dataset)
for i in range(len(dataset)-prediction_size):
    dataset_t_plus_prediction_step[i]= dataset[i-prediction_size]

# plot baseline and predictions
plt.figure(figsize=(10,4))
plt.plot(dataset)
plt.plot(PredictPlot)
plt.legend(('Data', 'Prediction'), fontsize=12)
plt.title(f'Simple NN forecast using {prediction_size} steps (1 seconds)', fontsize=20)
plt.xlabel('Time step', fontsize=16)
plt.ylabel('Wind Speed (m/s)', fontsize=16)
# plt.plot(scaler.inverse_transform(dataset_t_plus_prediction_step))

plt.figure(figsize=(10,4))
plt.plot(dataset-PredictPlot)
# plt.plot((scaler.inverse_transform(dataset))-scaler.inverse_transform(dataset_t_plus_prediction_step))

plt.figure(figsize=(10,4))
sns.distplot(errors, hist=False, color='blue')
plt.plot([RMSE_Score, RMSE_Score], [0, 1], color='darkblue')
plt.text(RMSE_Score, 0.5, f'RMSE: {RMSE_Score:.2f}', color='darkblue', fontsize=12, ha='center')
plt.plot([quantile_error, quantile_error], [0, 1], color='darkblue')
plt.text(quantile_error, 0.5, f'95% Quantile \n Error: {quantile_error:.2f}', color='darkblue', fontsize=12, ha='center')
plt.title(f'Probability Density Error of NN forecast using {prediction_size} steps (1 seconds)', fontsize=20)
# plt.legend(('Error'), fontsize=12)
plt.ylabel('Probability Density', fontsize=16)
plt.xlabel('Error (m/s)', fontsize=16)

plt.show()
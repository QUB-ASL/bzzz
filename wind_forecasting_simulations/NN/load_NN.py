
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

import keras
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

## Read Data
df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[3])

dataset = df_wind.values
dataset = df_wind.values.astype('float32')

scaler = MinMaxScaler(feature_range=(0, 1)) #Also try QuantileTransformer
dataset = scaler.fit_transform(dataset)

def to_sequences(dataset, seq_size=1):
    x = []
    y = []

    for i in range(len(dataset)-seq_size-prediction_size):
        #print(i)
        window = dataset[i:(i+seq_size), 0]
        x.append(window)
        y_outputs = dataset[(i+seq_size):(i+seq_size+prediction_size), 0]
        y.append(y_outputs)
        
    return np.array(x),np.array(y)

seq_size = 10
prediction_size = 40

X, Y = to_sequences(dataset, seq_size)

model = keras.saving.load_model("model.keras")

Predict = model.predict(X)

def get_last_prediction(data_set, prediction_size):
    output_array = []

    for i in range(len(data_set)):
        output = data_set[i][prediction_size-1]
        output_array.append(output)
    return np.array(output_array)

Predict = get_last_prediction(Predict, prediction_size)
Predict = np.reshape(Predict, (-1, 1))
Y = get_last_prediction(Y, prediction_size)

# Estimate model performance
#SInce we used minmaxscaler we can now use scaler.inverse_transform
#to invert the transformation.

Predict = scaler.inverse_transform(Predict)
Y_inverse = scaler.inverse_transform([Y])

# calculate root mean squared error
RMSE_Score = math.sqrt(mean_squared_error(Y_inverse[0], Predict[:,0]))
print('Prediction Score: %.2f RMSE' % (RMSE_Score))


# shift predictions for plotting
#we must shift the predictions so that they align on the x-axis with the original dataset. 
PredictPlot = np.empty_like(dataset)
PredictPlot[:, :] = np.nan
PredictPlot[seq_size:len(Predict)+seq_size, :] = Predict



# shift data for comparing plotting
dataset_t_plus_prediction_step = np.empty_like(dataset)
for i in range(len(dataset)-prediction_size):
    dataset_t_plus_prediction_step[i]= dataset[i-prediction_size]

# plot baseline and predictions
plt.figure(figsize=(10,4))
plt.plot(scaler.inverse_transform(dataset))
plt.plot(PredictPlot)
# plt.plot(scaler.inverse_transform(dataset_t_plus_prediction_step))

plt.figure(figsize=(10,4))
plt.plot((scaler.inverse_transform(dataset))-PredictPlot)
# plt.plot((scaler.inverse_transform(dataset))-scaler.inverse_transform(dataset_t_plus_prediction_step))
plt.show()
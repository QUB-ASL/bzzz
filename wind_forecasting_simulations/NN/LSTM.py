
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import csv
import time 

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator

def NN(file_name,
       input_size,
       prediction_horizon,
       no_of_epochs,
       Layer_2: bool,
       Layer_3: bool,
       Layer_4: bool,
       nodes_1,
       nodes_2,
       nodes_3,
       nodes_4 ):
    ## Read Data
    df_wind_U = pd.read_csv(f'{file_name}.csv', usecols=[7])
    df_wind_V = pd.read_csv(f'{file_name}.csv', usecols=[8])
    df_wind_W = pd.read_csv(f'{file_name}.csv', usecols=[9])

    dataset_U = df_wind_U.values
    dataset_U = df_wind_U.values.astype('float32')
    dataset_V = df_wind_V.values
    dataset_V = df_wind_V.values.astype('float32')
    dataset_W = df_wind_W.values
    dataset_W = df_wind_W.values.astype('float32')

    scaler_U = MinMaxScaler(feature_range=(0, 1)) #Also try QuantileTransformer
    scaler_V = MinMaxScaler(feature_range=(0, 1)) #Also try QuantileTransformer
    scaler_W = MinMaxScaler(feature_range=(0, 1)) #Also try QuantileTransformer
    dataset_U = scaler_U.fit_transform(dataset_U)
    dataset_V = scaler_V.fit_transform(dataset_V)
    dataset_W = scaler_W.fit_transform(dataset_W)

    train_size = int(len(dataset_U) * 0.66)
    train_U, test_U = dataset_U[0:train_size,:], dataset_U[train_size:len(dataset_U)-30,:]
    train_U_predict, test_U_predict = dataset_U[30:train_size+30,:], dataset_U[train_size+30:len(dataset_U),:]
    train_V, test_V = dataset_V[0:train_size,:], dataset_V[train_size:len(dataset_V)-30,:]
    train_V_predict, test_V_predict = dataset_V[30:train_size+30,:], dataset_V[train_size+30:len(dataset_V),:]
    train_W, test_W = dataset_W[0:train_size,:], dataset_W[train_size:len(dataset_W)-30,:]
    train_W_predict, test_W_predict = dataset_W[30:train_size+30,:], dataset_W[train_size+30:len(dataset_W),:]

    # print(train_U[:50])

    # define generator
    seq_size = input_size
    prediction_size = prediction_horizon
    U_train = TimeseriesGenerator(train_U, train_U_predict, length=seq_size, batch_size=1)
    V_train = TimeseriesGenerator(train_V, train_V_predict, length=seq_size, batch_size=1)
    W_train = TimeseriesGenerator(train_W, train_W_predict, length=seq_size, batch_size=1)
    U_test = TimeseriesGenerator(test_U, test_U_predict, length=seq_size, batch_size=1)
    V_test = TimeseriesGenerator(test_V, test_V_predict, length=seq_size, batch_size=1)
    W_test = TimeseriesGenerator(test_W, test_W_predict, length=seq_size, batch_size=1)

    # X,y = U_train[0]
    # print(f'Given the Array: \n{X.flatten()}')
    # print(f'Predict this y: \n {y}')
    # print(X.shape)

    #Input dimensions are... (N x seq_size)
    print('Build deep model...')
    # create and fit dense model
    model_U = Sequential()
    model_U.add(LSTM(nodes_1, input_shape=(seq_size,1), activation='relu')) 
    if Layer_2 is True:
          model_U.add(LSTM(nodes_2, activation='relu'))  
    if Layer_3 is True:
          model_U.add(LSTM(nodes_3, activation='relu'))  
    if Layer_4 is True:
          model_U.add(LSTM(nodes_4, activation='relu'))
    model_U.add(Dense(prediction_size))
    model_U.compile(loss='mean_squared_error', optimizer='adam', metrics = ['acc'])
    print(model_U.summary()) 

    model_U.fit(U_train, epochs=no_of_epochs)

    model_U.save("model_U.keras")

    model_V = Sequential()
    model_V.add(LSTM(nodes_1, input_shape=(seq_size,1), activation='relu')) 
    if Layer_2 is True:
          model_V.add(LSTM(nodes_2, activation='relu'))  
    if Layer_3 is True:
          model_V.add(LSTM(nodes_3, activation='relu'))   
    if Layer_4 is True:
          model_V.add(LSTM(nodes_4, activation='relu'))
    model_V.add(Dense(prediction_size))
    model_V.compile(loss='mean_squared_error', optimizer='adam', metrics = ['acc'])
    print(model_V.summary()) 

    model_V.fit(V_train, epochs=no_of_epochs)

    model_V.save("model_V.keras")

    model_W = Sequential()
    model_W.add(LSTM(nodes_1, input_shape=(seq_size,1), activation='relu')) 
    if Layer_2 is True:
          model_W.add(LSTM(nodes_2, activation='relu'))  
    if Layer_3 is True:
          model_W.add(LSTM(nodes_3, activation='relu'))  
    if Layer_4 is True:
          model_W.add(LSTM(nodes_4, activation='relu'))
    model_W.add(Dense(prediction_size))
    model_W.compile(loss='mean_squared_error', optimizer='adam', metrics = ['acc'])
    print(model_W.summary()) 

    model_W.fit(W_train, epochs=no_of_epochs)

    model_W.save("model_W.keras")

    trainPredict_U = model_U.predict(U_train)
    testPredict_U = model_U.predict(U_test)

    trainPredict_V = model_V.predict(V_train)
    testPredict_V = model_V.predict(U_test)

    trainPredict_W = model_W.predict(W_train)
    testPredict_W = model_W.predict(U_test)

    def get_last_prediction(data_set, prediction_size):
        output_array = []

        for i in range(len(data_set)):
            output = data_set[i][prediction_size-1]
            output_array.append(output)
        return np.array(output_array)

    trainPredict_U = get_last_prediction(trainPredict_U, prediction_size)
    trainPredict_U = np.reshape(trainPredict_U, (-1, 1))
    trainY_U = get_last_prediction(trainY_U, prediction_size)
    testPredict_U = get_last_prediction(testPredict_U, prediction_size)
    testPredict_U = np.reshape(testPredict_U, (-1, 1))
    testY_U = get_last_prediction(testY_U, prediction_size)

    trainPredict_V = get_last_prediction(trainPredict_V, prediction_size)
    trainPredict_V = np.reshape(trainPredict_V, (-1, 1))
    trainY_V = get_last_prediction(trainY_V, prediction_size)
    testPredict_V = get_last_prediction(testPredict_V, prediction_size)
    testPredict_V = np.reshape(testPredict_V, (-1, 1))
    testY_V = get_last_prediction(testY_V, prediction_size)

    trainPredict_W = get_last_prediction(trainPredict_W, prediction_size)
    trainPredict_W = np.reshape(trainPredict_W, (-1, 1))
    trainY_W = get_last_prediction(trainY_W, prediction_size)
    testPredict_W = get_last_prediction(testPredict_W, prediction_size)
    testPredict_W = np.reshape(testPredict_W, (-1, 1))
    testY_W = get_last_prediction(testY_W, prediction_size)

    # Estimate model performance
    #SInce we used minmaxscaler we can now use scaler.inverse_transform
    #to invert the transformation.

    trainPredict_U = scaler_U.inverse_transform(trainPredict_U)
    trainY_U_inverse = scaler_U.inverse_transform([trainY_U])
    testPredict_U = scaler_U.inverse_transform(testPredict_U)
    testY_U_inverse = scaler_U.inverse_transform([testY_U])

    trainPredict_V = scaler_V.inverse_transform(trainPredict_V)
    trainY_V_inverse = scaler_V.inverse_transform([trainY_V])
    testPredict_V = scaler_V.inverse_transform(testPredict_V)
    testY_V_inverse = scaler_V.inverse_transform([testY_V])

    trainPredict_W = scaler_W.inverse_transform(trainPredict_W)
    trainY_W_inverse = scaler_W.inverse_transform([trainY_W])
    testPredict_W = scaler_W.inverse_transform(testPredict_W)
    testY_W_inverse = scaler_W.inverse_transform([testY_W])

    # calculate root mean squared error
    trainScore_U = math.sqrt(mean_squared_error(trainY_U_inverse[0], trainPredict_U[:,0]))
    print('Train_U Score: %.2f RMSE' % (trainScore_U))

    testScore_U = math.sqrt(mean_squared_error(testY_U_inverse[0], testPredict_U[:,0]))
    print('Test_U Score: %.2f RMSE' % (testScore_U))

    trainScore_V = math.sqrt(mean_squared_error(trainY_V_inverse[0], trainPredict_V[:,0]))
    print('Train_V Score: %.2f RMSE' % (trainScore_V))

    testScore_V = math.sqrt(mean_squared_error(testY_V_inverse[0], testPredict_V[:,0]))
    print('Test_V Score: %.2f RMSE' % (testScore_V))

    trainScore_W = math.sqrt(mean_squared_error(trainY_W_inverse[0], trainPredict_W[:,0]))
    print('Train_W Score: %.2f RMSE' % (trainScore_W))

    testScore_W = math.sqrt(mean_squared_error(testY_W_inverse[0], testPredict_W[:,0]))
    print('Test_W Score: %.2f RMSE' % (testScore_W))

    # shift train predictions for plotting
    #we must shift the predictions so that they align on the x-axis with the original dataset. 
    trainPredictPlot_U = np.empty_like(dataset_U)
    trainPredictPlot_U[:, :] = np.nan
    trainPredictPlot_U[seq_size:len(trainPredict_U)+seq_size, :] = trainPredict_U

    trainPredictPlot_V = np.empty_like(dataset_V)
    trainPredictPlot_V[:, :] = np.nan
    trainPredictPlot_V[seq_size:len(trainPredict_V)+seq_size, :] = trainPredict_V

    trainPredictPlot_W = np.empty_like(dataset_W)
    trainPredictPlot_W[:, :] = np.nan
    trainPredictPlot_W[seq_size:len(trainPredict_W)+seq_size, :] = trainPredict_W

    # shift test predictions for plotting
    testPredictPlot_U = np.empty_like(dataset_U)
    testPredictPlot_U[:, :] = np.nan
    testPredictPlot_U[len(trainPredict_U)+(seq_size*2)+prediction_size:len(dataset_U)-prediction_size, :] = testPredict_U

    testPredictPlot_V = np.empty_like(dataset_V)
    testPredictPlot_V[:, :] = np.nan
    testPredictPlot_V[len(trainPredict_V)+(seq_size*2)+prediction_size:len(dataset_V)-prediction_size, :] = testPredict_V

    testPredictPlot_W = np.empty_like(dataset_W)
    testPredictPlot_W[:, :] = np.nan
    testPredictPlot_W[len(trainPredict_W)+(seq_size*2)+prediction_size:len(dataset_W)-prediction_size, :] = testPredict_W

    # shift data for comparing plotting
    df_wind_U
    df_wind_t_plus_prediction_step_U = np.empty_like(df_wind_U)
    df_wind_t_plus_prediction_step_V = np.empty_like(df_wind_V)
    df_wind_t_plus_prediction_step_W = np.empty_like(df_wind_W)
    for i in range(len(df_wind_U)-prediction_size):
        df_wind_t_plus_prediction_step_U[i]= df_wind_U.values[i-prediction_size]
        df_wind_t_plus_prediction_step_V[i]= df_wind_V.values[i-prediction_size]
        df_wind_t_plus_prediction_step_W[i]= df_wind_W.values[i-prediction_size]

    BenchmarkScore_U = math.sqrt(mean_squared_error(df_wind_U.values[:,0], df_wind_t_plus_prediction_step_U[:,0]))
    print('Benchmark_U Score: %.5f RMSE' % (BenchmarkScore_U))
    BenchmarkScore_V = math.sqrt(mean_squared_error(df_wind_V.values[:,0], df_wind_t_plus_prediction_step_U[:,0]))
    print('Benchmark_V Score: %.5f RMSE' % (BenchmarkScore_V))
    BenchmarkScore_W = math.sqrt(mean_squared_error(df_wind_W.values[:,0], df_wind_t_plus_prediction_step_U[:,0]))
    print('Benchmark_W Score: %.5f RMSE' % (BenchmarkScore_W))

    num_layers = 1
    if Layer_2 is True:
        num_layers = 2
    if Layer_3 is True:
        num_layers = 3

    with open(f'{file_name}_PH_{prediction_size}_RMSE_U.csv', "a+", newline="") as f:
                # creating the writer
                writer = csv.writer(f)
                # using writerow to write individual record one by one
                writer.writerow([f'Train_U_{num_layers}Layers_node1_{nodes_1}_node2_{nodes_2}_node3_{nodes_3}', trainScore_U])
                writer.writerow([f'Test_U_{num_layers}Layers_node1_{nodes_1}_node2_{nodes_2}_node3_{nodes_3}', testScore_U])

    with open(f'{file_name}_PH_{prediction_size}_RMSE_V.csv', "a+", newline="") as f:
                # creating the writer
                writer = csv.writer(f)
                # using writerow to write individual record one by one
                writer.writerow([f'Train_V_{num_layers}Layers_node1_{nodes_1}_node2_{nodes_2}_node3_{nodes_3}', trainScore_V])
                writer.writerow([f'Test_V_{num_layers}Layers_node1_{nodes_1}_node2_{nodes_2}_node3_{nodes_3}', testScore_V])

    with open(f'{file_name}_PH_{prediction_size}_RMSE_W.csv', "a+", newline="") as f:
                # creating the writer
                writer = csv.writer(f)
                # using writerow to write individual record one by one
                writer.writerow([f'Train_W_{num_layers}Layers_node1_{nodes_1}_node2_{nodes_2}_node3_{nodes_3}', trainScore_W])
                writer.writerow([f'Test_W_{num_layers}Layers_node1_{nodes_1}_node2_{nodes_2}_node3_{nodes_3}', testScore_W])

    # plot baseline and predictions
    plt.figure(figsize=(10,4))
    plt.title('U', fontsize=20)
    plt.plot(scaler_U.inverse_transform(dataset_U))
    plt.plot(trainPredictPlot_U)
    plt.plot(testPredictPlot_U)
    # plt.plot(scaler_U.inverse_transform(dataset_t_plus_prediction_step_U))

    plt.figure(figsize=(10,4))
    plt.title('U Error', fontsize=20)
    plt.plot((scaler_U.inverse_transform(dataset_U))-trainPredictPlot_U)
    plt.plot((scaler_U.inverse_transform(dataset_U))-testPredictPlot_U)
    # plt.plot((scaler_U.inverse_transform(dataset_U))-scaler.inverse_transform(dataset_t_plus_prediction_step_U))
    

    plt.figure(figsize=(10,4))
    plt.title('V', fontsize=20)
    plt.plot(scaler_V.inverse_transform(dataset_V))
    plt.plot(trainPredictPlot_V)
    plt.plot(testPredictPlot_V)
    # plt.plot(scaler_V.inverse_transform(dataset_t_plus_prediction_step_V))

    plt.figure(figsize=(10,4))
    plt.title('V Error', fontsize=20)
    plt.plot((scaler_V.inverse_transform(dataset_V))-trainPredictPlot_V)
    plt.plot((scaler_V.inverse_transform(dataset_V))-testPredictPlot_V)
    # plt.plot((scaler_V.inverse_transform(dataset_V))-scaler.inverse_transform(dataset_t_plus_prediction_step_V))


    plt.figure(figsize=(10,4))
    plt.title('W', fontsize=20)
    plt.plot(scaler_W.inverse_transform(dataset_W))
    plt.plot(trainPredictPlot_W)
    plt.plot(testPredictPlot_W)
    # plt.plot(scaler_W.inverse_transform(dataset_t_plus_prediction_step_W))

    plt.figure(figsize=(10,4))
    plt.title('W Error', fontsize=20)
    plt.plot((scaler_W.inverse_transform(dataset_W))-trainPredictPlot_W)
    plt.plot((scaler_W.inverse_transform(dataset_W))-testPredictPlot_W)
    # plt.plot((scaler_W.inverse_transform(dataset_W))-scaler.inverse_transform(dataset_t_plus_prediction_step_W))
    plt.show()

# for i in range(15,101,5):
#     NN(file_name = 'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10',
#         input_size = 10,
#         prediction_horizon = 40,
#         no_of_epochs = 10,
#         Layer_2 = False,
#         Layer_3 = False,
#         Layer_4 = False,
#         nodes_1 = i,
#         nodes_2 = 0,
#         nodes_3 = 0,
#         nodes_4 = 0 )
    # for j in range(5,101,5):
    #     NN(file_name = 'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10',
    #         input_size = 10,
    #         prediction_horizon = 40,
    #         no_of_epochs = 10,
    #         Layer_2 = True,
    #         Layer_3 = False,
    #         Layer_4 = False,
    #         nodes_1 = i,
    #         nodes_2 = j,
    #         nodes_3 = 0,
    #         nodes_4 = 0 )
    #     for k in range(5,101,5):
    #         NN(file_name = 'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10',
    #             input_size = 10,
    #             prediction_horizon = 40,
    #             no_of_epochs = 10,
    #             Layer_2 = True,
    #             Layer_3 = True,
    #             Layer_4 = False,
    #             nodes_1 = i,
    #             nodes_2 = j,
    #             nodes_3 = k,
    #             nodes_4 = 0 )
            # for l in range(5,101,5):
            #     NN(file_name = 'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10',
            #         input_size = 10,
            #         prediction_horizon = 40,
            #         no_of_epochs = 10,
            #         Layer_2 = True,
            #         Layer_3 = True,
            #         Layer_4 = True,
            #         nodes_1 = i,
            #         nodes_2 = j,
            #         nodes_3 = k,
            #         nodes_4 = l )


NN(file_name = 'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10',
    input_size = 10,
    prediction_horizon = 40,
    no_of_epochs = 1,
    Layer_2 = False,
    Layer_3 = False,
    Layer_4 = False,
    nodes_1 = 10,
    nodes_2 = 30,
    nodes_3 = 95,
    nodes_4 = 0 )
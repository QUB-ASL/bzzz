# import math
# import csv

# # Third-party imports
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import scipy.linalg as spla
# import seaborn as sns
# from sklearn.metrics import mean_squared_error

# # Local imports
# from online_kmeans import OnlineKMeans
# from NN_from_scratch import RBFNetworkQR

# def prepare_time_series_data(prediction_direction,
#                              x_wind,
#                              y_wind,
#                              z_wind,
#                              window_size, 
#                              prediction_horizon):
#     """
#     Prepare time series data for training.

#     :param prediction_direction: Prediction direction
#     :param x_wind: X-component of wind
#     :param y_wind: Y-component of wind
#     :param z_wind: Z-component of wind
#     :param window_size: Size of the window
#     :param prediction_horizon: Prediction horizon
#     :return: Prepared input and target data
#     """
#     X, y = [], []
#     for i in range(len(x_wind) - window_size - prediction_horizon):
#         X.append(list(y_wind[i:i+window_size][::-1]))
#         if prediction_direction == 'x':
#             y.append(x_wind[i+window_size+prediction_horizon-1])
#         elif prediction_direction == 'y':
#             y.append(y_wind[i+window_size+prediction_horizon-1])
#         elif prediction_direction == 'z':
#             y.append(z_wind[i+window_size+prediction_horizon-1])
#         else:
#             raise ValueError('Invalid prediction direction')
#     return np.array(X), np.array(y)

# # Example usage
# if __name__ == "__main__":

#     # Parameters for training and testing
#     window_size = 5
#     prediction_horizon = 10
#     number_of_initial_points = 400
#     adaptation_rate= 0.00000 # Adaptation rate for online K-means

#     # Read Data
#     df_wind = pd.read_csv('raspberry/data/Anemometer-16-04-25--11-51_N_10.csv')

#     x_wind = df_wind['U_axis'].values
#     y_wind = df_wind['V_axis'].values
#     z_wind = df_wind['W_axis'].values

#     # Prepare the time series data for RBF network
#     X, y = prepare_time_series_data(prediction_direction = 'y',
#                                     x_wind = x_wind,
#                                     y_wind = y_wind,
#                                     z_wind = z_wind,
#                                     window_size = window_size,
#                                     prediction_horizon = prediction_horizon)

#     X_predict = X[30000:]
#     y_predict = y[30000:]
#     print(f'X_predict: {X_predict}')
#     print(f'y_predict: {y_predict}')

#     # initial centers
#     centres_init = np.array([[1.71553333, 1.84766667, 2.00093333, 2.16166667, 2.32626667],
#                         [2.63985714, 2.71927143, 2.79192857, 2.86007143, 2.92562857],
#                         [2.5788381 , 2.54498095, 2.51198095, 2.48332381, 2.45959048],
#                         [2.37632414, 2.37241379, 2.37336552, 2.38013793, 2.39130345],
#                         [1.96415714, 1.96512857, 1.96387143, 1.96058571, 1.95415714],
#                         [2.42726   , 2.47073   , 2.52037   , 2.57133   , 2.61898   ],
#                         [2.26745455, 2.24070909, 2.21349091, 2.19029091, 2.17281818],
#                         [3.35703929, 3.36989643, 3.37571786, 3.37306071, 3.3579    ],
#                         [1.587175  , 1.559325  , 1.5565    , 1.582325  , 1.636525  ],
#                         [3.1511697 , 3.15440909, 3.15677273, 3.15889091, 3.16110909],
#                         [2.10166667, 2.08695   , 2.07808333, 2.07306667, 2.07305   ],
#                         [1.89646   , 1.8666    , 1.83914   , 1.81318   , 1.79398   ],
#                         [2.8151931 , 2.79592414, 2.7761931 , 2.75562069, 2.73335862],
#                         [2.64870303, 2.64579394, 2.6419697 , 2.63582424, 2.62806061],
#                         [3.00198   , 3.00438667, 3.00649   , 3.00800333, 3.00908   ]])
    
#     # initial weights
#     weights_init = np.array([ -78.19980768, -637.02184993, 2701.68486367, -1622.43524227,
#                         -192.05607422, 1264.79769918, -1439.76319725, 365.56463263,
#                         7.28361163, -2121.73872529, 1515.66936555, -128.65419325,
#                         -2378.20000548, -737.80777981, 3483.77633225])
    
#     # 1392 centers
#     centres_1392 = np.array([[5.4095    , 5.4435    , 5.6825    , 5.9525    , 6.1425    ],
#                              [3.92676667, 3.92215833, 3.91878333, 3.91561667, 3.91405   ],
#                              [4.36557692, 4.43873077, 4.5245    , 4.60973077, 4.67992308],
#                              [5.542     , 5.823     , 6.082     , 6.203     , 6.22      ],
#                              [6.162     , 6.169     , 5.899     , 5.608     , 5.38      ],
#                              [6.11116667, 6.15666667, 6.17      , 6.16433333, 6.11083333],
#                              [5.8162    , 5.673     , 5.4804    , 5.2718    , 5.071     ],
#                              [3.56630435, 3.55024638, 3.54317391, 3.54886957, 3.56413043],
#                              [4.69923077, 4.86538462, 5.03792308, 5.20007692, 5.31030769],
#                              [4.3126044 , 4.30804396, 4.30063736, 4.29337363, 4.28821978],
#                              [6.096     , 6.162     , 6.169     , 5.899     , 5.608     ],
#                              [4.94588235, 4.83011765, 4.70447059, 4.56082353, 4.43117647],
#                              [5.27526667, 5.26206667, 5.19813333, 5.11566667, 5.02853333],
#                              [5.40425   , 5.46608333, 5.51066667, 5.53966667, 5.5655    ],
#                              [3.05866667, 3.02166667, 3.01104762, 3.02557143, 3.06085714]])

#     # 1392 weights
#     weights_1392 = np.array([ -456.46786661,   250.24391023,    28.95253307,     4.25780845,
#   -506.70315449,   247.9347065,    844.91893609,  -119.25921228,
#    362.66273649,  -366.75881179,   -41.15449146,   433.69499191,
#  -1501.20672025,   804.74775874,    24.66340621])

#     # 2250 centers
#     centres_2250 = np.array([[5.4095    , 5.4435    , 5.6825    , 5.9525    , 6.1425    ],
#                              [3.92676667, 3.92215833, 3.91878333, 3.91561667, 3.91405   ],
#                              [4.36557692, 4.43873077, 4.5245    , 4.60973077, 4.67992308],
#                              [5.542     , 5.823     , 6.082     , 6.203     , 6.22      ],
#                              [6.162     , 6.169     , 5.899     , 5.608     , 5.38      ],
#                              [6.16958824, 6.20811765, 6.21921569, 6.21570588, 6.18901961],
#                              [5.8162    , 5.673     , 5.4804    , 5.2718    , 5.071     ],
#                              [3.56630435, 3.55024638, 3.54317391, 3.54886957, 3.56413043],
#                              [4.69923077, 4.86538462, 5.03792308, 5.20007692, 5.31030769],
#                              [4.3126044 , 4.30804396, 4.30063736, 4.29337363, 4.28821978],
#                              [6.096     , 6.162     , 6.169     , 5.899     , 5.608     ],
#                              [4.94588235, 4.83011765, 4.70447059, 4.56082353, 4.43117647],
#                              [5.27526667, 5.26206667, 5.19813333, 5.11566667, 5.02853333],
#                              [5.40425   , 5.46608333, 5.51066667, 5.53966667, 5.5655    ],
#                              [3.05866667, 3.02166667, 3.01104762, 3.02557143, 3.06085714],
#                              [7.8431157 , 7.83590083, 7.82626446, 7.81204959, 7.79765289],
#                              [6.82575556, 6.82586667, 6.82042222, 6.80411111, 6.78204444],
#                              [9.28806667, 9.3029    , 9.2769    , 9.21953333, 9.13433333]])
    
#     #2250 weights
#     weights_2250 = np.array([ 117.83355654,  243.62638974,  -10.5140975,   -97.0942315,   -92.61507084,
#     2.91271138,  198.24090122, -124.09572969,  134.80952306, -242.57384277,
#    70.46616721,  148.20163242, -273.89760209,  -91.17331614,   24.46002872,
#    -1.36843872,   12.32880494,    9.02514561])

#     # 2370 centers
#     centres_2370 = np.array([[5.4095    , 5.4435    , 5.6825    , 5.9525    , 6.1425    ],
#                              [3.92676667, 3.92215833, 3.91878333, 3.91561667, 3.91405   ],
#                              [4.36557692, 4.43873077, 4.5245    , 4.60973077, 4.67992308],
#                              [5.542     , 5.823     , 6.082     , 6.203     , 6.22      ],
#                              [6.162     , 6.169     , 5.899     , 5.608     , 5.38      ],
#                              [6.16958824, 6.20811765, 6.21921569, 6.21570588, 6.18901961],
#                              [5.8162    , 5.673     , 5.4804    , 5.2718    , 5.071     ],
#                              [3.56630435, 3.55024638, 3.54317391, 3.54886957, 3.56413043],
#                              [4.69923077, 4.86538462, 5.03792308, 5.20007692, 5.31030769],
#                              [4.3126044 , 4.30804396, 4.30063736, 4.29337363, 4.28821978],
#                              [6.096     , 6.162     , 6.169     , 5.899     , 5.608     ],
#                              [4.94588235, 4.83011765, 4.70447059, 4.56082353, 4.43117647],
#                              [5.27526667, 5.26206667, 5.19813333, 5.11566667, 5.02853333],
#                              [5.40425   , 5.46608333, 5.51066667, 5.53966667, 5.5655    ],
#                              [3.05866667, 3.02166667, 3.01104762, 3.02557143, 3.06085714],
#                              [7.8431157 , 7.83590083, 7.82626446, 7.81204959, 7.79765289],
#                              [6.82575556, 6.82586667, 6.82042222, 6.80411111, 6.78204444],
#                              [9.28806667, 9.3029    , 9.2769    , 9.21953333, 9.13433333]])
    
#     # 2370 weights
#     weights_2370 = np.array([  72.47376544,  235.02797292,    1.67292208,  -75.39203714,  -85.19847622,
#     0.90592913,  203.94883934, -118.95854638,  129.67748197, -248.40597454,
#    45.95619918,  165.36296444, -332.912236,    -12.33738067,   23.75118001,
#    -1.4495689,    14.81039559,    8.63197318])  
    
#     centres_last = np.array([[5.4095    , 5.4435    , 5.6825    , 5.9525    , 6.1425    ],
#                              [3.92676667, 3.92215833, 3.91878333, 3.91561667, 3.91405   ],
#                              [4.36557692, 4.43873077, 4.5245    , 4.60973077, 4.67992308],
#                              [5.542     , 5.823     , 6.082     , 6.203     , 6.22      ],
#                              [6.162     , 6.169     , 5.899     , 5.608     , 5.38      ],
#                              [6.16958824, 6.20811765, 6.21921569, 6.21570588, 6.18901961],
#                              [5.8162    , 5.673     , 5.4804    , 5.2718    , 5.071     ],
#                              [3.56630435, 3.55024638, 3.54317391, 3.54886957, 3.56413043],
#                              [4.69923077, 4.86538462, 5.03792308, 5.20007692, 5.31030769],
#                              [4.3126044 , 4.30804396, 4.30063736, 4.29337363, 4.28821978],
#                              [6.096     , 6.162     , 6.169     , 5.899     , 5.608     ],
#                              [4.94588235, 4.83011765, 4.70447059, 4.56082353, 4.43117647],
#                              [5.27526667, 5.26206667, 5.19813333, 5.11566667, 5.02853333],
#                              [5.40425   , 5.46608333, 5.51066667, 5.53966667, 5.5655    ],
#                              [3.05866667, 3.02166667, 3.01104762, 3.02557143, 3.06085714],
#                              [7.8431157 , 7.83590083, 7.82626446, 7.81204959, 7.79765289],
#                              [6.82575556, 6.82586667, 6.82042222, 6.80411111, 6.78204444],
#                              [9.28806667, 9.3029    , 9.2769    , 9.21953333, 9.13433333]])
    
#     weights_last = np.array([  93.98027113,  147.02974868,  -42.78829612,  -87.58448899,  -90.84219297,
#     2.26156099,  181.83966756,  -86.96698102,  108.29691174, -108.93893595,
#    57.1361583,    97.58664547, -240.77655082,  -46.26448438,   20.09451453,
#    -1.46321978,   14.70369684,    8.50470663])
    
#     print(centres_1392.shape[0])

#     # Initialize online K-means with 5 clusters
#     online_kmeans_init = OnlineKMeans(n_clusters=centres_init.shape[0], 
#                                  adaptation_rate=adaptation_rate,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.5, 
#                                  random_state=42,
#                                  initial_centers=centres_init)
#     initial_centers_init = online_kmeans_init.initialise_centres()
#     # print(f'initial_centers: {initial_centers}')
    
#     # Initialize and train the RBF network using QR decomposition
#     rbf_net_init = RBFNetworkQR(num_centers=centres_init.shape[0], 
#                            centers=initial_centers_init,
#                            weights=weights_init)
    

#     # Initialize online K-means with 5 clusters
#     online_kmeans_1392 = OnlineKMeans(n_clusters=centres_1392.shape[0],
#                                  adaptation_rate=adaptation_rate,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.5, 
#                                  random_state=42,
#                                  initial_centers=centres_1392)
#     initial_centers_1392 = online_kmeans_1392.initialise_centres()
#     # print(f'initial_centers: {initial_centers}')
    
#     # Initialize and train the RBF network using QR decomposition
#     rbf_net_1392 = RBFNetworkQR(num_centers=centres_1392.shape[0],
#                            centers=initial_centers_1392,
#                            weights=weights_1392)
    
#     # Initialize online K-means with 5 clusters
#     online_kmeans_2250 = OnlineKMeans(n_clusters=centres_2250.shape[0],
#                                  adaptation_rate=adaptation_rate,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.5, 
#                                  random_state=42,
#                                  initial_centers=centres_2250)
#     initial_centers_2250 = online_kmeans_2250.initialise_centres()
#     # print(f'initial_centers: {initial_centers}')
    
#     # Initialize and train the RBF network using QR decomposition
#     rbf_net_2250 = RBFNetworkQR(num_centers=centres_2250.shape[0], 
#                            centers=initial_centers_2250,
#                            weights=weights_2250)
    
#     # Initialize online K-means with 5 clusters
#     online_kmeans_2370 = OnlineKMeans(n_clusters=centres_2370.shape[0], 
#                                  adaptation_rate=adaptation_rate,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.5, 
#                                  random_state=42,
#                                  initial_centers=centres_2370)
#     initial_centers_2370 = online_kmeans_2370.initialise_centres()
#     # print(f'initial_centers: {initial_centers}')
    
#     # Initialize and train the RBF network using QR decomposition
#     rbf_net_2370 = RBFNetworkQR(num_centers=centres_2370.shape[0], 
#                            centers=initial_centers_2370,
#                            weights=weights_2370)
    

#      # Initialize online K-means with 5 clusters
#     online_kmeans_last = OnlineKMeans(n_clusters=centres_last.shape[0], 
#                                  adaptation_rate=adaptation_rate,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.5, 
#                                  random_state=42,
#                                  initial_centers=centres_last)
#     initial_centers_last = online_kmeans_last.initialise_centres()
#     # print(f'initial_centers: {initial_centers}')
    
#     # Initialize and train the RBF network using QR decomposition
#     rbf_net_last = RBFNetworkQR(num_centers=centres_last.shape[0], 
#                            centers=initial_centers_last,
#                            weights=weights_last)
    

#     # print(f'weights: {rbf_net.weights}')
#     # print(f'centers: {rbf_net.centers}')
#     # print(f'initial')
#     store_predictions_init = []
#     store_predictions_1392 = []
#     store_predictions_2250 = []
#     store_predictions_2370 = []
#     store_predictions_last = []
#     for i in range(len(X_predict)):
#         prediction_init = rbf_net_init.predict(X_predict[i].reshape(1, -1))[0]
#         store_predictions_init.append(prediction_init)

#         prediction_1392 = rbf_net_1392.predict(X_predict[i].reshape(1, -1))[0]
#         store_predictions_1392.append(prediction_1392)

#         prediction_2250 = rbf_net_2250.predict(X_predict[i].reshape(1, -1))[0]
#         store_predictions_2250.append(prediction_2250)

#         prediction_2370 = rbf_net_2370.predict(X_predict[i].reshape(1, -1))[0]
#         store_predictions_2370.append(prediction_2370)

#         prediction_last = rbf_net_last.predict(X_predict[i].reshape(1, -1))[0]
#         store_predictions_last.append(prediction_last)
        
#     # print(f'prediction: {store_predictions_1392}')

#     plt.figure(figsize=(10,4))
#     plt.plot(y_predict, label='wind speed', color='black', linewidth=2)
#     plt.plot(store_predictions_init, label='RBFNN prediction', color='red', linestyle='--', linewidth=1)
#     plt.plot(store_predictions_1392, label='RBFNN prediction', color='blue', linestyle='--', linewidth=1)
#     plt.plot(store_predictions_2250, label='RBFNN prediction', color='green', linestyle='--', linewidth=1)
#     plt.plot(store_predictions_2370, label='RBFNN prediction', color='purple', linestyle='--', linewidth=1)
#     plt.plot(store_predictions_last, label='RBFNN prediction', color='orange', linestyle='--', linewidth=1)
#     plt.title('RBFNN prediction of wind speed over time', fontsize=32)
#     plt.legend(fontsize=20)
#     plt.ylabel('Wind Speed (m/s)', fontsize=23)
#     plt.xlabel('Time', fontsize=23)
#     plt.show()
    



# import math
# import csv

# # Third-party imports
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import scipy.linalg as spla
# import seaborn as sns
# from sklearn.metrics import mean_squared_error

# # Local imports
# from online_kmeans import OnlineKMeans
# from NN_from_scratch import RBFNetworkQR

# def prepare_time_series_data(prediction_direction,
#                              x_wind,
#                              y_wind,
#                              z_wind,
#                              window_size, 
#                              prediction_horizon):
#     """
#     Prepare time series data for training.

#     :param prediction_direction: Prediction direction
#     :param x_wind: X-component of wind
#     :param y_wind: Y-component of wind
#     :param z_wind: Z-component of wind
#     :param window_size: Size of the window
#     :param prediction_horizon: Prediction horizon
#     :return: Prepared input and target data
#     """
#     X, y = [], []
#     for i in range(len(x_wind) - window_size - prediction_horizon):
#         X.append(list(y_wind[i:i+window_size][::-1]))
#         if prediction_direction == 'x':
#             y.append(x_wind[i+window_size+prediction_horizon-1])
#         elif prediction_direction == 'y':
#             y.append(y_wind[i+window_size+prediction_horizon-1])
#         elif prediction_direction == 'z':
#             y.append(z_wind[i+window_size+prediction_horizon-1])
#         else:
#             raise ValueError('Invalid prediction direction')
#     return np.array(X), np.array(y)

# # Example usage
# if __name__ == "__main__":

#     # Parameters for training and testing
#     window_size = 5
#     prediction_horizon = 10
#     number_of_initial_points = 400
#     adaptation_rate= 0.00000 # Adaptation rate for online K-means

#     # Read Data
#     df_wind = pd.read_csv('raspberry/data/Anemometer-16-04-25--11-51_N_10.csv')

#     x_wind = df_wind['U_axis'].values
#     y_wind = df_wind['V_axis'].values
#     z_wind = df_wind['W_axis'].values

#     # Prepare the time series data for RBF network
#     X, y = prepare_time_series_data(prediction_direction = 'y',
#                                     x_wind = x_wind,
#                                     y_wind = y_wind,
#                                     z_wind = z_wind,
#                                     window_size = window_size,
#                                     prediction_horizon = prediction_horizon)

#     X_predict = X[30000:]
#     y_predict = y[30000:]
#     print(f'X_predict: {X_predict}')
#     print(f'y_predict: {y_predict}')

#     # initial centers
#     centres_init = np.array([[1.71553333, 1.84766667, 2.00093333, 2.16166667, 2.32626667],
#                         [2.63985714, 2.71927143, 2.79192857, 2.86007143, 2.92562857],
#                         [2.5788381 , 2.54498095, 2.51198095, 2.48332381, 2.45959048],
#                         [2.37632414, 2.37241379, 2.37336552, 2.38013793, 2.39130345],
#                         [1.96415714, 1.96512857, 1.96387143, 1.96058571, 1.95415714],
#                         [2.42726   , 2.47073   , 2.52037   , 2.57133   , 2.61898   ],
#                         [2.26745455, 2.24070909, 2.21349091, 2.19029091, 2.17281818],
#                         [3.35703929, 3.36989643, 3.37571786, 3.37306071, 3.3579    ],
#                         [1.587175  , 1.559325  , 1.5565    , 1.582325  , 1.636525  ],
#                         [3.1511697 , 3.15440909, 3.15677273, 3.15889091, 3.16110909],
#                         [2.10166667, 2.08695   , 2.07808333, 2.07306667, 2.07305   ],
#                         [1.89646   , 1.8666    , 1.83914   , 1.81318   , 1.79398   ],
#                         [2.8151931 , 2.79592414, 2.7761931 , 2.75562069, 2.73335862],
#                         [2.64870303, 2.64579394, 2.6419697 , 2.63582424, 2.62806061],
#                         [3.00198   , 3.00438667, 3.00649   , 3.00800333, 3.00908   ]])
    
#     # initial weights
#     weights_init = np.array([ -78.19980768, -637.02184993, 2701.68486367, -1622.43524227,
#                         -192.05607422, 1264.79769918, -1439.76319725, 365.56463263,
#                         7.28361163, -2121.73872529, 1515.66936555, -128.65419325,
#                         -2378.20000548, -737.80777981, 3483.77633225])
    
#     # 1392 centers
#     centres_1392 = np.array([[5.4095    , 5.4435    , 5.6825    , 5.9525    , 6.1425    ],
#                              [3.92676667, 3.92215833, 3.91878333, 3.91561667, 3.91405   ],
#                              [4.36557692, 4.43873077, 4.5245    , 4.60973077, 4.67992308],
#                              [5.542     , 5.823     , 6.082     , 6.203     , 6.22      ],
#                              [6.162     , 6.169     , 5.899     , 5.608     , 5.38      ],
#                              [6.11116667, 6.15666667, 6.17      , 6.16433333, 6.11083333],
#                              [5.8162    , 5.673     , 5.4804    , 5.2718    , 5.071     ],
#                              [3.56630435, 3.55024638, 3.54317391, 3.54886957, 3.56413043],
#                              [4.69923077, 4.86538462, 5.03792308, 5.20007692, 5.31030769],
#                              [4.3126044 , 4.30804396, 4.30063736, 4.29337363, 4.28821978],
#                              [6.096     , 6.162     , 6.169     , 5.899     , 5.608     ],
#                              [4.94588235, 4.83011765, 4.70447059, 4.56082353, 4.43117647],
#                              [5.27526667, 5.26206667, 5.19813333, 5.11566667, 5.02853333],
#                              [5.40425   , 5.46608333, 5.51066667, 5.53966667, 5.5655    ],
#                              [3.05866667, 3.02166667, 3.01104762, 3.02557143, 3.06085714]])

#     # 1392 weights
#     weights_1392 = np.array([ -456.46786661,   250.24391023,    28.95253307,     4.25780845,
#   -506.70315449,   247.9347065,    844.91893609,  -119.25921228,
#    362.66273649,  -366.75881179,   -41.15449146,   433.69499191,
#  -1501.20672025,   804.74775874,    24.66340621])

#     # 2250 centers
#     centres_2250 = np.array([[5.4095    , 5.4435    , 5.6825    , 5.9525    , 6.1425    ],
#                              [3.92676667, 3.92215833, 3.91878333, 3.91561667, 3.91405   ],
#                              [4.36557692, 4.43873077, 4.5245    , 4.60973077, 4.67992308],
#                              [5.542     , 5.823     , 6.082     , 6.203     , 6.22      ],
#                              [6.162     , 6.169     , 5.899     , 5.608     , 5.38      ],
#                              [6.16958824, 6.20811765, 6.21921569, 6.21570588, 6.18901961],
#                              [5.8162    , 5.673     , 5.4804    , 5.2718    , 5.071     ],
#                              [3.56630435, 3.55024638, 3.54317391, 3.54886957, 3.56413043],
#                              [4.69923077, 4.86538462, 5.03792308, 5.20007692, 5.31030769],
#                              [4.3126044 , 4.30804396, 4.30063736, 4.29337363, 4.28821978],
#                              [6.096     , 6.162     , 6.169     , 5.899     , 5.608     ],
#                              [4.94588235, 4.83011765, 4.70447059, 4.56082353, 4.43117647],
#                              [5.27526667, 5.26206667, 5.19813333, 5.11566667, 5.02853333],
#                              [5.40425   , 5.46608333, 5.51066667, 5.53966667, 5.5655    ],
#                              [3.05866667, 3.02166667, 3.01104762, 3.02557143, 3.06085714],
#                              [7.8431157 , 7.83590083, 7.82626446, 7.81204959, 7.79765289],
#                              [6.82575556, 6.82586667, 6.82042222, 6.80411111, 6.78204444],
#                              [9.28806667, 9.3029    , 9.2769    , 9.21953333, 9.13433333]])
    
#     #2250 weights
#     weights_2250 = np.array([ 117.83355654,  243.62638974,  -10.5140975,   -97.0942315,   -92.61507084,
#     2.91271138,  198.24090122, -124.09572969,  134.80952306, -242.57384277,
#    70.46616721,  148.20163242, -273.89760209,  -91.17331614,   24.46002872,
#    -1.36843872,   12.32880494,    9.02514561])

#     # 2370 centers
#     centres_2370 = np.array([[5.4095    , 5.4435    , 5.6825    , 5.9525    , 6.1425    ],
#                              [3.92676667, 3.92215833, 3.91878333, 3.91561667, 3.91405   ],
#                              [4.36557692, 4.43873077, 4.5245    , 4.60973077, 4.67992308],
#                              [5.542     , 5.823     , 6.082     , 6.203     , 6.22      ],
#                              [6.162     , 6.169     , 5.899     , 5.608     , 5.38      ],
#                              [6.16958824, 6.20811765, 6.21921569, 6.21570588, 6.18901961],
#                              [5.8162    , 5.673     , 5.4804    , 5.2718    , 5.071     ],
#                              [3.56630435, 3.55024638, 3.54317391, 3.54886957, 3.56413043],
#                              [4.69923077, 4.86538462, 5.03792308, 5.20007692, 5.31030769],
#                              [4.3126044 , 4.30804396, 4.30063736, 4.29337363, 4.28821978],
#                              [6.096     , 6.162     , 6.169     , 5.899     , 5.608     ],
#                              [4.94588235, 4.83011765, 4.70447059, 4.56082353, 4.43117647],
#                              [5.27526667, 5.26206667, 5.19813333, 5.11566667, 5.02853333],
#                              [5.40425   , 5.46608333, 5.51066667, 5.53966667, 5.5655    ],
#                              [3.05866667, 3.02166667, 3.01104762, 3.02557143, 3.06085714],
#                              [7.8431157 , 7.83590083, 7.82626446, 7.81204959, 7.79765289],
#                              [6.82575556, 6.82586667, 6.82042222, 6.80411111, 6.78204444],
#                              [9.28806667, 9.3029    , 9.2769    , 9.21953333, 9.13433333]])
    
#     # 2370 weights
#     weights_2370 = np.array([  72.47376544,  235.02797292,    1.67292208,  -75.39203714,  -85.19847622,
#     0.90592913,  203.94883934, -118.95854638,  129.67748197, -248.40597454,
#    45.95619918,  165.36296444, -332.912236,    -12.33738067,   23.75118001,
#    -1.4495689,    14.81039559,    8.63197318])  
    
#     centres_last = np.array([[5.4095    , 5.4435    , 5.6825    , 5.9525    , 6.1425    ],
#                              [3.92676667, 3.92215833, 3.91878333, 3.91561667, 3.91405   ],
#                              [4.36557692, 4.43873077, 4.5245    , 4.60973077, 4.67992308],
#                              [5.542     , 5.823     , 6.082     , 6.203     , 6.22      ],
#                              [6.162     , 6.169     , 5.899     , 5.608     , 5.38      ],
#                              [6.16958824, 6.20811765, 6.21921569, 6.21570588, 6.18901961],
#                              [5.8162    , 5.673     , 5.4804    , 5.2718    , 5.071     ],
#                              [3.56630435, 3.55024638, 3.54317391, 3.54886957, 3.56413043],
#                              [4.69923077, 4.86538462, 5.03792308, 5.20007692, 5.31030769],
#                              [4.3126044 , 4.30804396, 4.30063736, 4.29337363, 4.28821978],
#                              [6.096     , 6.162     , 6.169     , 5.899     , 5.608     ],
#                              [4.94588235, 4.83011765, 4.70447059, 4.56082353, 4.43117647],
#                              [5.27526667, 5.26206667, 5.19813333, 5.11566667, 5.02853333],
#                              [5.40425   , 5.46608333, 5.51066667, 5.53966667, 5.5655    ],
#                              [3.05866667, 3.02166667, 3.01104762, 3.02557143, 3.06085714],
#                              [7.8431157 , 7.83590083, 7.82626446, 7.81204959, 7.79765289],
#                              [6.82575556, 6.82586667, 6.82042222, 6.80411111, 6.78204444],
#                              [9.28806667, 9.3029    , 9.2769    , 9.21953333, 9.13433333]])
    
#     weights_last = np.array([  93.98027113,  147.02974868,  -42.78829612,  -87.58448899,  -90.84219297,
#     2.26156099,  181.83966756,  -86.96698102,  108.29691174, -108.93893595,
#    57.1361583,    97.58664547, -240.77655082,  -46.26448438,   20.09451453,
#    -1.46321978,   14.70369684,    8.50470663])
    
#     print(centres_1392.shape[0])

#     # Initialize online K-means with 5 clusters
#     online_kmeans_init = OnlineKMeans(n_clusters=centres_init.shape[0], 
#                                  adaptation_rate=adaptation_rate,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.5, 
#                                  random_state=42,
#                                  initial_centers=centres_init)
#     initial_centers_init = online_kmeans_init.initialise_centres()
#     # print(f'initial_centers: {initial_centers}')
    
#     # Initialize and train the RBF network using QR decomposition
#     rbf_net_init = RBFNetworkQR(num_centers=centres_init.shape[0], 
#                            sigma=2.4414121234298647,
#                            centers=initial_centers_init,
#                            weights=weights_init)
    

#     # Initialize online K-means with 5 clusters
#     online_kmeans_1392 = OnlineKMeans(n_clusters=centres_1392.shape[0],
#                                  adaptation_rate=adaptation_rate,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.5, 
#                                  random_state=42,
#                                  initial_centers=centres_1392)
#     initial_centers_1392 = online_kmeans_1392.initialise_centres()
#     # print(f'initial_centers: {initial_centers}')
    
#     # Initialize and train the RBF network using QR decomposition
#     rbf_net_1392 = RBFNetworkQR(num_centers=centres_1392.shape[0],
#                            sigma=2.4414121234298647,
#                            centers=initial_centers_1392,
#                            weights=weights_1392)
    
#     # Initialize online K-means with 5 clusters
#     online_kmeans_2250 = OnlineKMeans(n_clusters=centres_2250.shape[0],
#                                  adaptation_rate=adaptation_rate,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.5, 
#                                  random_state=42,
#                                  initial_centers=centres_2250)
#     initial_centers_2250 = online_kmeans_2250.initialise_centres()
#     # print(f'initial_centers: {initial_centers}')
    
#     # Initialize and train the RBF network using QR decomposition
#     rbf_net_2250 = RBFNetworkQR(num_centers=centres_2250.shape[0], 
#                            sigma=2.4414121234298647,
#                            centers=initial_centers_2250,
#                            weights=weights_2250)
    
#     # Initialize online K-means with 5 clusters
#     online_kmeans_2370 = OnlineKMeans(n_clusters=centres_2370.shape[0], 
#                                  adaptation_rate=adaptation_rate,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.5, 
#                                  random_state=42,
#                                  initial_centers=centres_2370)
#     initial_centers_2370 = online_kmeans_2370.initialise_centres()
#     # print(f'initial_centers: {initial_centers}')
    
#     # Initialize and train the RBF network using QR decomposition
#     rbf_net_2370 = RBFNetworkQR(num_centers=centres_2370.shape[0], 
#                            sigma=2.4414121234298647,
#                            centers=initial_centers_2370,
#                            weights=weights_2370)
    

#      # Initialize online K-means with 5 clusters
#     online_kmeans_last = OnlineKMeans(n_clusters=centres_last.shape[0], 
#                                  adaptation_rate=adaptation_rate,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.5, 
#                                  random_state=42,
#                                  initial_centers=centres_last)
#     initial_centers_last = online_kmeans_last.initialise_centres()
#     # print(f'initial_centers: {initial_centers}')
    
#     # Initialize and train the RBF network using QR decomposition
#     rbf_net_last = RBFNetworkQR(num_centers=centres_last.shape[0], 
#                            sigma=2.4414121234298647,
#                            centers=initial_centers_last,
#                            weights=weights_last)
    

#     # print(f'weights: {rbf_net.weights}')
#     # print(f'centers: {rbf_net.centers}')
#     # print(f'initial')
#     store_predictions_init = []
#     store_predictions_1392 = []
#     store_predictions_2250 = []
#     store_predictions_2370 = []
#     store_predictions_last = []
#     for i in range(len(X_predict)):
#         prediction_init = rbf_net_init.predict(X_predict[i].reshape(1, -1))[0]
#         store_predictions_init.append(prediction_init)

#         prediction_1392 = rbf_net_1392.predict(X_predict[i].reshape(1, -1))[0]
#         store_predictions_1392.append(prediction_1392)

#         prediction_2250 = rbf_net_2250.predict(X_predict[i].reshape(1, -1))[0]
#         store_predictions_2250.append(prediction_2250)

#         prediction_2370 = rbf_net_2370.predict(X_predict[i].reshape(1, -1))[0]
#         store_predictions_2370.append(prediction_2370)

#         prediction_last = rbf_net_last.predict(X_predict[i].reshape(1, -1))[0]
#         store_predictions_last.append(prediction_last)
        
#     # print(f'prediction: {store_predictions_1392}')

#     plt.figure(figsize=(10,4))
#     plt.plot(y_predict, label='wind speed', color='black', linewidth=2)
#     plt.plot(store_predictions_init, label='RBFNN prediction', color='red', linestyle='--', linewidth=1)
#     plt.plot(store_predictions_1392, label='RBFNN prediction', color='blue', linestyle='--', linewidth=1)
#     plt.plot(store_predictions_2250, label='RBFNN prediction', color='green', linestyle='--', linewidth=1)
#     plt.plot(store_predictions_2370, label='RBFNN prediction', color='purple', linestyle='--', linewidth=1)
#     plt.plot(store_predictions_last, label='RBFNN prediction', color='orange', linestyle='--', linewidth=1)
#     plt.title('RBFNN prediction of wind speed over time', fontsize=32)
#     plt.legend(fontsize=20)
#     plt.ylabel('Wind Speed (m/s)', fontsize=23)
#     plt.xlabel('Time', fontsize=23)
#     plt.show()
    



# import matplotlib.pyplot as plt 
# import pandas as pd

# file = pd.read_csv("raspberry/data/GNSS-16-04-25--12-11.csv")

# # find the average latitude and longitude between the given number lines of csv file
# line_numbers = [196, 772, 872, 1051]

# average_latitude = []
# average_longitude = []
# plot_latitude = []
# plot_longitude = []
# for i in range(len(line_numbers)):
#     plot_latitude.append(file.Lat[line_numbers[i]])
#     plot_longitude.append(file.Lon[line_numbers[i]])
#     if i == 0:
#         average_latitude.append(file.Lat[0:line_numbers[i]].mean())
#         average_longitude.append(file.Lon[0:line_numbers[i]].mean())
#     else:
#         average_latitude.append(file.Lat[line_numbers[i-1]:line_numbers[i]].mean())
#         average_longitude.append(file.Lon[line_numbers[i-1]:line_numbers[i]].mean())

# # print(average_latitude)
# # print(average_longitude)

# plt.figure(figsize = (10, 6))
# #plt.plot(file.Date_Time, file.Altitude)
# #plt.plot(file.Date_Time, file.Latitude)
# #plt.plot(file.Date_Time, file.Longitude)
# plt.plot(file.Lat, file.Lon)
# plt.plot(file.Lat[0], file.Lon[0], 'ro', markersize=5, c='purple', label='Start point')
# plt.plot(file.Lat[880], file.Lon[880], 'ro', markersize=5, c='yellow', label='End point')
# plt.plot(file.Lat[980], file.Lon[980], 'ro', markersize=5, c='yellow', label='End point')
# # plt.plot(file.Lat[931], file.Lon[931], 'ro', markersize=5, c='red', label='End point')
# # plt.plot(file.Lat[998], file.Lon[998], 'ro', markersize=5, c='red', label='End point')
# # plt.plot(file.Lat[1202], file.Lon[1202], 'ro', markersize=5, c='red', label='End point')

# print(file.Lat[1622])
# print(file.Lon[1622])


# # lat = [54.578895166666676,54.57889550000001,54.578784000000006,54.57876433333333,54.578748,54.57876855555556,
# #        54.57879416666666,54.57881916666667,54.578834,54.57883883333333,54.57878233333333]
# # long = [-5.929909500000001,-5.92991,-5.929832833333333,-5.929815166666667,-5.929785833333334,-5.929731777777778,
# #         -5.929737500000001,-5.929851666666667,-5.929863833333333,-5.929897999999999,-5.929948833333332]

# plt.plot(plot_latitude, plot_longitude, 'ro', markersize=5, c='red', label='GPS points')
# plt.plot(average_latitude, average_longitude, 'ro', markersize=5, c='green', label='Average GPS points')
# # plt.plot(54.57880, -5.929838, 'ro', markersize=5, c='purple', label='Start point')

# # plt.title('Altitude')
# #plt.xlabel('Date_time')


# # plt.xticks([])
# # plt.ylabel('Altitude')
# plt.grid(True)
# # plt.legend()

# print(file.Latitude)
# print(file.Longitude)

# fig = plt.figure(figsize=(10, 6))
# ax = fig.add_subplot(projection='3d')

# ax.plot(file.Lat, file.Lon, file.Height, label='3D line')

# plt.figure(figsize=(10, 6))
# plt.plot(file.N, file.E)

# fig2 = plt.figure(figsize=(10, 6))
# ax2 = fig2.add_subplot(projection='3d')
# ax2.plot(file.N, file.E, -file.D, label='3D line')
# ax2.set_xlim3d(-40, 40)
# ax2.set_ylim3d(-40, 40)
# ax2.set_zlim3d(-40, 40)


# plt.show()


# import math
# import csv

# # Third-party imports
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import scipy.linalg as spla
# import seaborn as sns
# from sklearn.metrics import mean_squared_error

# # Local imports
# from online_kmeans import OnlineKMeans
# from NN_from_scratch import RBFNetworkQR
# from interpolation_between_points import Kriging

# def prepare_time_series_data(prediction_direction,
#                              x_wind,
#                              y_wind,
#                              z_wind,
#                              window_size, 
#                              prediction_horizon):
#     """
#     Prepare time series data for training.

#     :param prediction_direction: Prediction direction
#     :param x_wind: X-component of wind
#     :param y_wind: Y-component of wind
#     :param z_wind: Z-component of wind
#     :param window_size: Size of the window
#     :param prediction_horizon: Prediction horizon
#     :return: Prepared input and target data
#     """
#     X, y = [], []
#     for i in range(len(x_wind) - window_size - prediction_horizon):
#         X.append(list(y_wind[i:i+window_size][::-1]))
#         if prediction_direction == 'x':
#             y.append(x_wind[i+window_size+prediction_horizon-1])
#         elif prediction_direction == 'y':
#             y.append(y_wind[i+window_size+prediction_horizon-1])
#         elif prediction_direction == 'z':
#             y.append(z_wind[i+window_size+prediction_horizon-1])
#         else:
#             raise ValueError('Invalid prediction direction')
#     return np.array(X), np.array(y)

# # Example usage
# if __name__ == "__main__":

#     # Parameters for training and testing
#     window_size = 5
#     prediction_horizon = 10
#     number_of_initial_points = 400
#     adaptation_rate= 0.00000 # Adaptation rate for online K-means

#     # Read Data
#     df_wind = pd.read_csv('raspberry/data/Anemometer-15-03-24--16-44_N_10.csv')

#     x_wind = df_wind['U_axis'].values
#     y_wind = df_wind['V_axis'].values
#     z_wind = df_wind['W_axis'].values

#     # Prepare the time series data for RBF network
#     X, y = prepare_time_series_data(prediction_direction = 'y',
#                                     x_wind = x_wind,
#                                     y_wind = y_wind,
#                                     z_wind = z_wind,
#                                     window_size = window_size,
#                                     prediction_horizon = prediction_horizon)

#     X_predict = X[1281:1321]
#     y_predict = y[1281:1321]
#     # print(f'X_predict: {X_predict}')
#     # print(f'y_predict: {y_predict}')

#     # initial centers
#     centres_init = np.array([[1.71553333, 1.84766667, 2.00093333, 2.16166667, 2.32626667],
#                         [2.63985714, 2.71927143, 2.79192857, 2.86007143, 2.92562857],
#                         [2.5788381 , 2.54498095, 2.51198095, 2.48332381, 2.45959048],
#                         [2.37632414, 2.37241379, 2.37336552, 2.38013793, 2.39130345],
#                         [1.96415714, 1.96512857, 1.96387143, 1.96058571, 1.95415714],
#                         [2.42726   , 2.47073   , 2.52037   , 2.57133   , 2.61898   ],
#                         [2.26745455, 2.24070909, 2.21349091, 2.19029091, 2.17281818],
#                         [3.35703929, 3.36989643, 3.37571786, 3.37306071, 3.3579    ],
#                         [1.587175  , 1.559325  , 1.5565    , 1.582325  , 1.636525  ],
#                         [3.1511697 , 3.15440909, 3.15677273, 3.15889091, 3.16110909],
#                         [2.10166667, 2.08695   , 2.07808333, 2.07306667, 2.07305   ],
#                         [1.89646   , 1.8666    , 1.83914   , 1.81318   , 1.79398   ],
#                         [2.8151931 , 2.79592414, 2.7761931 , 2.75562069, 2.73335862],
#                         [2.64870303, 2.64579394, 2.6419697 , 2.63582424, 2.62806061],
#                         [3.00198   , 3.00438667, 3.00649   , 3.00800333, 3.00908   ]])
    
#     # initial weights
#     weights_init = np.array([ -78.19980768, -637.02184993, 2701.68486367, -1622.43524227,
#                         -192.05607422, 1264.79769918, -1439.76319725, 365.56463263,
#                         7.28361163, -2121.73872529, 1515.66936555, -128.65419325,
#                         -2378.20000548, -737.80777981, 3483.77633225])
    
#     # 1392 centers
#     centres_1392 = np.array([[1.71553333, 1.84766667, 2.00093333, 2.16166667, 2.32626667],
#                         [2.63985714, 2.71927143, 2.79192857, 2.86007143, 2.92562857],
#                         [2.5788381 , 2.54498095, 2.51198095, 2.48332381, 2.45959048],
#                         [2.37632414, 2.37241379, 2.37336552, 2.38013793, 2.39130345],
#                         [1.96415714, 1.96512857, 1.96387143, 1.96058571, 1.95415714],
#                         [2.42726   , 2.47073   , 2.52037   , 2.57133   , 2.61898   ],
#                         [2.26745455, 2.24070909, 2.21349091, 2.19029091, 2.17281818],
#                         [3.36712836, 3.37432836, 3.37359701, 3.36405672, 3.34255522],
#                         [1.587175  , 1.559325  , 1.5565    , 1.582325  , 1.636525  ],
#                         [3.1511697 , 3.15440909, 3.15677273, 3.15889091, 3.16110909],
#                         [2.10166667, 2.08695   , 2.07808333, 2.07306667, 2.07305   ],
#                         [1.89646   , 1.8666    , 1.83914   , 1.81318   , 1.79398   ],
#                         [2.8151931 , 2.79592414, 2.7761931 , 2.75562069, 2.73335862],
#                         [2.64870303, 2.64579394, 2.6419697 , 2.63582424, 2.62806061],
#                         [3.00198   , 3.00438667, 3.00649   , 3.00800333, 3.00908   ],
#                         [3.78527   , 3.798125  , 3.79494   , 3.77355   , 3.73485   ],
#                         [4.46772   , 4.41234   , 4.35548   , 4.29712   , 4.2387    ]])

#     # 1392 weights
#     weights_1392 = np.array([ -109.39238526, -637.44181387, 3022.60262533, -4082.40210868,
#                         -1282.14352558, 2026.20830508, -1656.72708969, -13.18795054,
#                         150.44859064,  -341.44272543,  3982.35902767,  -454.02136877,
#                         -1925.66207875,    61.54976333,  1266.16559013,    -5.50740275,
#                         9.33999613])

#     # 2250 centers
#     centres_2250 = np.array([[1.71553333, 1.84766667, 2.00093333, 2.16166667, 2.32626667],
#                         [2.63985714, 2.71927143, 2.79192857, 2.86007143, 2.92562857],
#                         [2.5788381 , 2.54498095, 2.51198095, 2.48332381, 2.45959048],
#                         [2.37632414, 2.37241379, 2.37336552, 2.38013793, 2.39130345],
#                         [1.96415714, 1.96512857, 1.96387143, 1.96058571, 1.95415714],
#                         [2.42726   , 2.47073   , 2.52037   , 2.57133   , 2.61898   ],
#                         [2.26745455, 2.24070909, 2.21349091, 2.19029091, 2.17281818],
#                         [3.36712836, 3.37432836, 3.37359701, 3.36405672, 3.34255522],
#                         [1.587175  , 1.559325  , 1.5565    , 1.582325  , 1.636525  ],
#                         [3.1511697 , 3.15440909, 3.15677273, 3.15889091, 3.16110909],
#                         [2.10166667, 2.08695   , 2.07808333, 2.07306667, 2.07305   ],
#                         [1.89646   , 1.8666    , 1.83914   , 1.81318   , 1.79398   ],
#                         [2.8151931 , 2.79592414, 2.7761931 , 2.75562069, 2.73335862],
#                         [2.64870303, 2.64579394, 2.6419697 , 2.63582424, 2.62806061],
#                         [3.00198   , 3.00438667, 3.00649   , 3.00800333, 3.00908   ],
#                         [3.78527   , 3.798125  , 3.79494   , 3.77355   , 3.73485   ],
#                         [4.89608817, 4.87716344, 4.85724516, 4.8362129 , 4.81405161],
#                         [7.26876842, 7.29756842, 7.31308421, 7.31314737, 7.29546316],
#                         [6.282915  , 6.27715   , 6.267235  , 6.2535    , 6.23676   ]])
    
#     #2250 weights
#     weights_2250 = np.array([ -68.77831532, -16.03390769, 1478.44730895, -838.98404019,
#                         -530.57886538, 618.71621536, -1108.20754525, 26.78726447,
#                         58.93253738, -225.25441059, 1651.40831018, -134.94056919,
#                         -51.7542495, -1248.3242445, 393.45180588, 3.098841,
#                         4.56128518, 5.24842882, 5.14398449])

#     # 2370 centers
#     centres_2370 = np.array([[1.71553333, 1.84766667, 2.00093333, 2.16166667, 2.32626667],
#                         [2.63985714, 2.71927143, 2.79192857, 2.86007143, 2.92562857],
#                         [2.5788381 , 2.54498095, 2.51198095, 2.48332381, 2.45959048],
#                         [2.37632414, 2.37241379, 2.37336552, 2.38013793, 2.39130345],
#                         [1.96415714, 1.96512857, 1.96387143, 1.96058571, 1.95415714],
#                         [2.42726   , 2.47073   , 2.52037   , 2.57133   , 2.61898   ],
#                         [2.26745455, 2.24070909, 2.21349091, 2.19029091, 2.17281818],
#                         [3.36712836, 3.37432836, 3.37359701, 3.36405672, 3.34255522],
#                         [1.587175  , 1.559325  , 1.5565    , 1.582325  , 1.636525  ],
#                         [3.1511697 , 3.15440909, 3.15677273, 3.15889091, 3.16110909],
#                         [2.10166667, 2.08695   , 2.07808333, 2.07306667, 2.07305   ],
#                         [1.89646   , 1.8666    , 1.83914   , 1.81318   , 1.79398   ],
#                         [2.8151931 , 2.79592414, 2.7761931 , 2.75562069, 2.73335862],
#                         [2.64870303, 2.64579394, 2.6419697 , 2.63582424, 2.62806061],
#                         [3.00198   , 3.00438667, 3.00649   , 3.00800333, 3.00908   ],
#                         [3.78527   , 3.798125  , 3.79494   , 3.77355   , 3.73485   ],
#                         [4.89608817, 4.87716344, 4.85724516, 4.8362129 , 4.81405161],
#                         [7.26876842, 7.29756842, 7.31308421, 7.31314737, 7.29546316],
#                         [6.282915  , 6.27715   , 6.267235  , 6.2535    , 6.23676   ]])
    
#     # 2370 weights
#     weights_2370 = np.array([ -21.00797434, -165.55249191, 1644.5978958, -1417.12583152,
#                         -613.78511136, 888.41891857, -756.55514247, 12.76521567,
#                         40.76042209, -309.37577483, 1485.33727112, -43.64600905,
#                         -461.83967755, -971.67567786, 693.96959509,  6.59383453,
#                         4.35647557, 5.20074325, 5.20212823])  
    
#     print(centres_1392.shape[0])

#     # Initialize online K-means with 5 clusters
#     online_kmeans_init = OnlineKMeans(n_clusters=centres_init.shape[0], 
#                                  adaptation_rate=adaptation_rate,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.5, 
#                                  random_state=42,
#                                  initial_centers=centres_init)
#     initial_centers_init = online_kmeans_init.initialise_centres()
#     # print(f'initial_centers: {initial_centers}')
    
#     # Initialize and train the RBF network using QR decomposition
#     rbf_net_init = RBFNetworkQR(num_centers=centres_init.shape[0], 
#                                 sigma=1.292301791863947,
#                            centers=initial_centers_init,
#                            weights=weights_init)
    

#     # Initialize online K-means with 5 clusters
#     online_kmeans_1392 = OnlineKMeans(n_clusters=centres_1392.shape[0],
#                                  adaptation_rate=adaptation_rate,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.5, 
#                                  random_state=42,
#                                  initial_centers=centres_1392)
#     initial_centers_1392 = online_kmeans_1392.initialise_centres()
#     # print(f'initial_centers: {initial_centers}')
    
#     # Initialize and train the RBF network using QR decomposition
#     rbf_net_1392 = RBFNetworkQR(num_centers=centres_1392.shape[0],
#                                 sigma=1.292301791863947,
#                            centers=initial_centers_1392,
#                            weights=weights_1392)
    
#     # Initialize online K-means with 5 clusters
#     online_kmeans_2250 = OnlineKMeans(n_clusters=centres_2250.shape[0],
#                                  adaptation_rate=adaptation_rate,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.5, 
#                                  random_state=42,
#                                  initial_centers=centres_2250)
#     initial_centers_2250 = online_kmeans_2250.initialise_centres()
#     # print(f'initial_centers: {initial_centers}')
    
#     # Initialize and train the RBF network using QR decomposition
#     rbf_net_2250 = RBFNetworkQR(num_centers=centres_2250.shape[0], 
#                                 sigma=1.292301791863947,
#                            centers=initial_centers_2250,
#                            weights=weights_2250)
    
#     # Initialize online K-means with 5 clusters
#     online_kmeans_2370 = OnlineKMeans(n_clusters=centres_2370.shape[0], 
#                                  adaptation_rate=adaptation_rate,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.5, 
#                                  random_state=42,
#                                  initial_centers=centres_2370)
#     initial_centers_2370 = online_kmeans_2370.initialise_centres()
#     # print(f'initial_centers: {initial_centers}')
    
#     # Initialize and train the RBF network using QR decomposition
#     rbf_net_2370 = RBFNetworkQR(num_centers=centres_2370.shape[0], 
#                                 sigma=1.292301791863947,
#                            centers=initial_centers_2370,
#                            weights=weights_2370)
    

#     # print(f'weights: {rbf_net.weights}')
#     # print(f'centers: {rbf_net.centers}')
#     # print(f'initial')

    

#     store_predictions_init = []
#     store_predictions_1392 = []
#     store_predictions_2250 = []
#     store_predictions_2370 = []
#     for i in range(len(X_predict)):
#         prediction_init = rbf_net_init.predict(X_predict[i].reshape(1, -1))[0]
#         store_predictions_init.append(prediction_init)

#         prediction_1392 = rbf_net_1392.predict(X_predict[i].reshape(1, -1))[0]
#         store_predictions_1392.append(prediction_1392)

#         prediction_2250 = rbf_net_2250.predict(X_predict[i].reshape(1, -1))[0]
#         store_predictions_2250.append(prediction_2250)

#         prediction_2370 = rbf_net_2370.predict(X_predict[i].reshape(1, -1))[0]
#         store_predictions_2370.append(prediction_2370)
        
#     print(f'prediction: {store_predictions_1392}')

#     Kriging = Kriging(sigma2=0.01, zeta=0.001)

#     # 3 known locations (x, y)
#     known_locs = np.array([[54.57878143478261, -5.929830528985507],
#                         [54.57880292364533, -5.929791606732348],
#                         [54.578830124413145 , -5.92986525117371]])
#     query_loc = np.array([54.57880, -5.929838])

#     estimate = []
    
#     # Their known values
#     for i in range(len(store_predictions_1392)):
#         known_values = np.array([store_predictions_1392[i],
#                                 store_predictions_2250[i],
#                                 store_predictions_2370[i]])
#         # Perform Kriging interpolation
#         estimate.append(Kriging.interpolate(known_locs, known_values, query_loc))


#     plt.figure(figsize=(10,4))
#     plt.plot(y_predict, label='wind speed', color='black', linewidth=2)
#     # plt.plot(store_predictions_init, label='RBFNN prediction', color='red', linestyle='--', linewidth=1)
#     plt.plot(store_predictions_1392, label='RBFNN prediction', color='blue', linestyle='--', linewidth=1)
#     plt.plot(store_predictions_2250, label='RBFNN prediction', color='green', linestyle='--', linewidth=1)
#     plt.plot(store_predictions_2370, label='RBFNN prediction', color='purple', linestyle='--', linewidth=1)
#     plt.plot(estimate, label='Kriging prediction', color='orange', linestyle='--', linewidth=1)
#     plt.title('RBFNN prediction of wind speed over time', fontsize=32)
#     plt.legend(fontsize=20)
#     plt.ylabel('Wind Speed (m/s)', fontsize=23)
#     plt.xlabel('Time', fontsize=23)
#     plt.show()
    





#############################################################################################################################################






import matplotlib.pyplot as plt 
import pandas as pd

file = pd.read_csv("raspberry/data/GNSS-16-04-25--12-11.csv")

# find the average latitude and longitude between the given number lines of csv file
line_numbers = [196, 772, 872, 1051]

average_latitude = []
average_longitude = []
plot_latitude = []
plot_longitude = []
for i in range(len(line_numbers)):
    plot_latitude.append(file.N[line_numbers[i]])
    plot_longitude.append(file.E[line_numbers[i]])
    if i == 0:
        average_latitude.append(file.N[0:line_numbers[i]].mean())
        average_longitude.append(file.E[0:line_numbers[i]].mean())
    else:
        average_latitude.append(file.N[line_numbers[i-1]:line_numbers[i]].mean())
        average_longitude.append(file.E[line_numbers[i-1]:line_numbers[i]].mean())

print(average_latitude)
print(average_longitude)

plt.figure(figsize = (10, 6))
#plt.plot(file.Date_Time, file.Altitude)
#plt.plot(file.Date_Time, file.Latitude)
#plt.plot(file.Date_Time, file.Longitude)
plt.plot(file.N, file.E, label='Trajectory', linewidth=3)
plt.plot(file.N[0], file.E[0], 'ro', markersize=15, c='purple', label='Start point')
plt.plot(-1.7, 0 , 'ro', markersize=15, c='tab:orange', label='Where to forecast')
# plt.plot(file.Lat[880], file.Lon[880], 'ro', markersize=5, c='yellow', label='End point')
# plt.plot(file.Lat[980], file.Lon[980], 'ro', markersize=5, c='yellow', label='End point')
# plt.plot(file.Lat[931], file.Lon[931], 'ro', markersize=5, c='red', label='End point')
# plt.plot(file.Lat[998], file.Lon[998], 'ro', markersize=5, c='red', label='End point')
# plt.plot(file.Lat[1202], file.Lon[1202], 'ro', markersize=5, c='red', label='End point')

# print(file.Lat[1622])
# print(file.Lon[1622])


# lat = [54.578895166666676,54.57889550000001,54.578784000000006,54.57876433333333,54.578748,54.57876855555556,
#        54.57879416666666,54.57881916666667,54.578834,54.57883883333333,54.57878233333333]
# long = [-5.929909500000001,-5.92991,-5.929832833333333,-5.929815166666667,-5.929785833333334,-5.929731777777778,
#         -5.929737500000001,-5.929851666666667,-5.929863833333333,-5.929897999999999,-5.929948833333332]

plt.plot(plot_latitude, plot_longitude, 'ro', markersize=15, c='red', label='New model')
plt.plot(average_latitude, average_longitude, 'ro', markersize=15, c='green', label='center of the model')
# plt.plot(54.57880, -5.929838, 'ro', markersize=5, c='purple', label='Start point')

# plt.title('Altitude')
#plt.xlabel('Date_time')


# plt.xticks([])
# plt.ylabel('Altitude')
plt.grid(True)
plt.legend(loc='upper right', fontsize=20)
plt.xlabel('North (m)', fontsize=23)
plt.ylabel('East (m)', fontsize=23)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.title('Model locations', fontsize=32)

# print(file.Latitude)
# print(file.Longitude)

# fig = plt.figure(figsize=(10, 6))
# ax = fig.add_subplot(projection='3d')

# ax.plot(file.Lat, file.Lon, file.Height, label='3D line')

# plt.figure(figsize=(10, 6))
# plt.plot(file.N, file.E)

# fig2 = plt.figure(figsize=(10, 6))
# ax2 = fig2.add_subplot(projection='3d')
# ax2.plot(file.N, file.E, -file.D, label='3D line')
# ax2.set_xlim3d(-40, 40)
# ax2.set_ylim3d(-40, 40)
# ax2.set_zlim3d(-40, 40)


plt.show()
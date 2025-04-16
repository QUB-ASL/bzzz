########## RBF NN QR decomposition to solve the 
########## least squares problem with rank-1 update 

# Standard library imports
import math
import csv

# Third-party imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.linalg as spla
import seaborn as sns
from sklearn.metrics import mean_squared_error

# Local imports
from online_kmeans import OnlineKMeans


class RBFNetworkQR:
    """
    Radial Basis Function Network using QR decomposition to solve the least 
    squares problem with rank-1 update.
    """
    def __init__(self, 
                 num_centers, 
                 sigma=None, 
                 centers=None, 
                 regulariser=None,
                 weights = None):
        """
        Initialize the RBF Network.

        :param num_centers: Number of RBF centers
        :param sigma: Width of RBF kernels
        :param centers: RBF centers (initialized later)
        :param regulariser: Regularization parameter
        """
        self.num_centers = num_centers
        self.centers = centers
        self.regulariser = regulariser
        self.weights = weights
        self.Q = None
        self.R = None
        self.b = None
        self.I = np.eye(num_centers)
        self.X = None
        self.y = None
        self.A = None
        self.apply_learning_rate = 0

        # If sigma is not specified, calculate it based on the distances 
        # between centers
        if sigma is None:
            dists = np.linalg.norm(self.centers[:, np.newaxis] 
                                   - self.centers, axis=2)
            self.sigma = np.mean(dists)
        else:
            self.sigma = sigma

    def _rbf_function(self, x, center):
        """
        Gaussian RBF function.

        :param x: Input vector
        :param center: Center of the RBF
        :return: RBF value
        """
        return np.exp(-np.linalg.norm(x - center) ** 2 / (2 * self.sigma ** 2))

    def _calculate_A(self, X):
        """
        Calculate the design matrix A using the RBF function.

        :param X: Input data
        :return: Design matrix A
        """
        n_samples = X.shape[0]
        A = np.zeros((n_samples, self.num_centers))
        for i in range(n_samples):
            for j in range(self.num_centers):
                A[i, j] = self._rbf_function(X[i], self.centers[j])
        return A

    def fit(self, X, y):
        """
        Fit the RBF Network to the data.

        :param X: Input data
        :param y: Target values
        """
        A = self._calculate_A(X)
        # Solve for the weights using QR decomposition
        self.Q, self.R = np.linalg.qr(A.T @ A + self.regulariser * self.I)
        self.b = A.T @ y
        rhs = self.Q.T @ self.b
        lhs = self.R 
        self.weights = spla.solve_triangular(lhs, rhs)
        self.X = X
        self.y = y
        self.A = A

    def update(self, 
            new_X, 
            new_y, 
            updated_centers,
            max_num_measures=None,
            last_split_cluster_idx=None):
        """
        Update the RBF Network with a new sample and regulariser.

        :param new_X: New input sample
        :param new_y: New target value
        :param updated_centers: Updated RBF centers
        """

        # Check if the number of centers has changed
        if len(updated_centers) != self.num_centers:
            # print(f'last split cluster index: {last_split_cluster_idx}')
            # Append a new column and row to Q and R for the new center
            new_column_in_A = np.zeros((self.X.shape[0], 1))
            for i in range(self.X.shape[0]):
                 new_column_in_A[i] = self._rbf_function(self.X[i], updated_centers[-1])
            new_column_in_ATA = self.A.T @ new_column_in_A
            self.A = np.hstack((self.A, new_column_in_A))
            new_row_in_ATA = new_column_in_A.T @ self.A
            new_row_in_ATA[0, -1] = new_row_in_ATA[0, -1] + self.regulariser 

            # Update the number of centers
            self.num_centers = len(updated_centers)
            self.I = np.eye(self.num_centers)
            self.centers = updated_centers

            self.Q, self.R = spla.qr_insert(self.Q, self.R, new_column_in_ATA, self.num_centers - 1, 'col')
            self.Q, self.R = spla.qr_insert(self.Q, self.R, new_row_in_ATA, self.num_centers - 1, 'row')
            new_b = new_column_in_A.T @ self.y
            self.b = np.append(self.b, new_b)

            self.weights = np.append(self.weights, 0)
            self.apply_learning_rate = 20

        else:
            self.centers = updated_centers

        # Compute the RBF activation for the new sample new_X
        new_A = self._calculate_A(new_X.reshape(1, -1))
        new_A = new_A.reshape(-1)

        # Append new sample
        self.X = np.vstack((self.X, new_X))
        self.y = np.append(self.y, new_y)
        self.A = np.vstack((self.A, new_A))

        # Update the QR decomposition using rank-1 update
        self.Q, self.R = spla.qr_update(self.Q, self.R, new_A, new_A)

        # Update the b vector
        self.b = self.b + new_y * new_A

            # If limit exceeded, remove oldest sample
        if max_num_measures is not None and len(self.y) > max_num_measures:
            # Oldest sample
            a_old = self.A[0]
            y_old = self.y[0]

            # Downdate QR
            self.Q, self.R = spla.qr_update(self.Q, self.R, -a_old, a_old)

            # Update b
            self.b = self.b - y_old * a_old

            # Remove from stored data
            self.X = self.X[1:]
            self.y = self.y[1:]
            self.A = self.A[1:]

        # Solve for updated weights
        rhs = self.Q.T @ self.b
        lhs = self.R
        new_weights = spla.solve_triangular(lhs, rhs)

        if self.apply_learning_rate > 0:
            learning_rate = np.ones(self.num_centers)
            learning_rate = 0.01
            self.weights = (1 - learning_rate) * self.weights + learning_rate * new_weights
            self.apply_learning_rate -= 1
        else:
            self.weights = new_weights

    def predict(self, X):
        """
        Predict the output for new inputs.

        :param X: Input data
        :return: Predicted values
        """
        A = self._calculate_A(X)
        return np.dot(A, self.weights)


# def prepare_time_series_data(series, 
#                              window_size, 
#                              prediction_horizon):
#     """
#     Prepare time series data for training.

#     :param series: Time series data
#     :param window_size: Size of the window
#     :param prediction_horizon: Prediction horizon
#     :return: Prepared input and target data
#     """
#     X, y = [], []
#     for i in range(len(series) - window_size - prediction_horizon):
#         X.append(series[i+window_size:i:-1])
#         y.append(series[i + window_size + prediction_horizon])
#     return np.array(X), np.array(y)
# y_wind[i:i+window_size][::-1]


def prepare_time_series_data(prediction_direction,
                             x_wind,
                             y_wind,
                             z_wind,
                             window_size, 
                             prediction_horizon):
    """
    Prepare time series data for training.

    :param prediction_direction: Prediction direction
    :param x_wind: X-component of wind
    :param y_wind: Y-component of wind
    :param z_wind: Z-component of wind
    :param window_size: Size of the window
    :param prediction_horizon: Prediction horizon
    :return: Prepared input and target data
    """
    X, y = [], []
    for i in range(len(x_wind) - window_size - prediction_horizon):
        X.append(list(y_wind[i:i+window_size][::-1]))
        if prediction_direction == 'x':
            y.append(x_wind[i+window_size+prediction_horizon-1])
        elif prediction_direction == 'y':
            y.append(y_wind[i+window_size+prediction_horizon-1])
        elif prediction_direction == 'z':
            y.append(z_wind[i+window_size+prediction_horizon-1])
        else:
            raise ValueError('Invalid prediction direction')
    return np.array(X), np.array(y)

def NN(file_name, 
       window_size, 
       num_centers,
       adaptation_rate,
       regulariser, 
       prediction_horizon):
    """
    Train and evaluate the RBF Network for wind forecasting.

    :param file_name: Name of the CSV file containing the data
    :param window_size: Size of the window
    :param num_centers: Number of RBF centers
    :param regulariser: Regularization parameter
    :param prediction_horizon: Prediction horizon
    """
    # Read Data
    df_wind_U = pd.read_csv(f'{file_name}.csv', usecols=[7])
    df_wind_V = pd.read_csv(f'{file_name}.csv', usecols=[8])
    df_wind_W = pd.read_csv(f'{file_name}.csv', usecols=[9])

    series_U = df_wind_U.values.reshape(-1)
    series_V = df_wind_V.values.reshape(-1)
    series_W = df_wind_W.values.reshape(-1)
    
    X_U, y_U = prepare_time_series_data(series_U, 
                                        window_size, 
                                        prediction_horizon)
    X_V, y_V = prepare_time_series_data(series_V, 
                                        window_size, 
                                        prediction_horizon)
    X_W, y_W = prepare_time_series_data(series_W, 
                                        window_size, 
                                        prediction_horizon)

    # Initialize online K-means with 5 clusters
    online_kmeans = OnlineKMeans(n_clusters=num_centers, 
                                 adaptation_rate=adaptation_rate,
                                 random_state=42)
    # Determine the centers for U, V, and W components
    U_centers = online_kmeans.initialise_centres(X_U)
    V_centers = online_kmeans.initialise_centres(X_V)
    W_centers = online_kmeans.initialise_centres(X_W)

    # Initialize and train the RBF network using QR decomposition
    rbf_net_U = RBFNetworkQR(num_centers=num_centers, 
                           centers=U_centers,
                           regulariser=regulariser)
    rbf_net_U.fit(X_U, y_U)
    rbf_net_V = RBFNetworkQR(num_centers=num_centers, 
                           centers=V_centers,
                           regulariser=regulariser)
    rbf_net_V.fit(X_V, y_V)
    rbf_net_W = RBFNetworkQR(num_centers=num_centers, 
                           centers=W_centers,
                           regulariser=regulariser)
    rbf_net_W.fit(X_W, y_W)

    y_pred_U = []
    y_pred_V = []
    y_pred_W = []
    for i in range(X_U.shape[0]):
        y_pred_U.append(rbf_net_U.predict(X_U[i].reshape(1, -1))[0])
        y_pred_V.append(rbf_net_V.predict(X_V[i].reshape(1, -1))[0])
        y_pred_W.append(rbf_net_W.predict(X_W[i].reshape(1, -1))[0])

    trainScore_U = math.sqrt(mean_squared_error(y_U, y_pred_U))
    print('trainScore_U Score: %.5f RMSE' % (trainScore_U))
    trainScore_V = math.sqrt(mean_squared_error(y_V, y_pred_V))
    print('trainScore_V Score: %.5f RMSE' % (trainScore_V))
    trainScore_W = math.sqrt(mean_squared_error(y_W, y_pred_W))
    print('trainScore_W Score: %.5f RMSE' % (trainScore_W))

    print(f'rbf_U_centers: {U_centers}')
    print(f'rbf_U_weights: {rbf_net_U.weights}')

    # Generate implicit x-values
    t = np.arange(len(series_U))

    # Plot the true time series and the 10th step ahead predictions
    plt.figure(figsize=(12, 6))
    plt.plot(t, series_U, label='True Time Series', color='blue')
    plt.plot(t[prediction_horizon + window_size:], y_pred_U, label='10th Step Ahead Prediction', color='red', linestyle='--')
    plt.title('10th Step Ahead Time Series Prediction using RBF Neural Network (QR Decomposition)', fontsize=32)
    plt.xlabel('Time', fontsize=23)
    plt.ylabel('Value', fontsize=23)
    plt.legend(fontsize=20)
    plt.show()

    # with open(f'{file_name}_RBF_NN_PH_{prediction_horizon}_RMSE_U.csv',
    #           "a+", newline="") as f:
    #             writer = csv.writer(f)
    #             writer.writerow([f'Train_U_Window_size_{window_size}_Number_of_centers_{num_centers}', trainScore_U])

    # with open(f'{file_name}_RBF_NN_PH_{prediction_horizon}_RMSE_V.csv',
    #           "a+", newline="") as f:
    #             writer = csv.writer(f)
    #             writer.writerow([f'Train_V_Window_size_{window_size}_Number_of_centers_{num_centers}', trainScore_V])

    # with open(f'{file_name}_RBF_NN_PH_{prediction_horizon}_RMSE_W.csv',
    #           "a+", newline="") as f:
    #             writer = csv.writer(f)
    #             writer.writerow([f'Train_W_Window_size_{window_size}_Number_of_centers_{num_centers}', trainScore_W])

# Example usage
if __name__ == "__main__":

    # Parameters for training and testing
    window_size = 5
    prediction_horizon = 10
    number_of_initial_points = 400
    num_centers = 15  # Number of RBF centers
    adaptation_rate= 0.00000 # Adaptation rate for online K-means
    regulariser = 0.05 # Regularization parameter
    max_num_measures = 2400

    # Read Data
    df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv')

    x_wind = df_wind['U_axis'].values
    y_wind = df_wind['V_axis'].values
    z_wind = df_wind['W_axis'].values

    # Prepare the time series data for RBF network
    X, y = prepare_time_series_data(prediction_direction = 'y',
                                    x_wind = x_wind,
                                    y_wind = y_wind,
                                    z_wind = z_wind,
                                    window_size = window_size,
                                    prediction_horizon = prediction_horizon)

    # Split the data: first number of initial points for initial fit, 
    # rest for updates
    X_initial = X[:number_of_initial_points]
    y_initial = y[:number_of_initial_points]
    X_update = X[number_of_initial_points:]
    y_update = y[number_of_initial_points:]
    X_predict = X[number_of_initial_points + prediction_horizon:]
    y_predict = y[number_of_initial_points + prediction_horizon:]

    # PH 10 centers
    centres = np.array([[ 0.53071695,  0.52723016,  0.52596789,  0.52685064,  0.53004222],
                        [ 4.00688486,  4.01560888,  4.01861806,  4.01658023,  4.0093508 ],
                        [-1.66841888, -1.6686613 , -1.66871117, -1.66843386, -1.66799753],
                        [ 2.32090368,  2.31076418,  2.30733048,  2.31064987,  2.32065954],
                        [-4.12364366, -4.1468606 , -4.1554303 , -4.14808247, -4.12476244],
                        [ 6.41950779,  6.45587749,  6.46839827,  6.45659264,  6.4208329 ],
                        [-0.78802573, -0.78892308, -0.78930183, -0.78914221, -0.78836263],
                        [ 3.43983729,  3.43795472,  3.43679842,  3.43619495,  3.43604542],
                        [ 1.73288376,  1.7243838 ,  1.72140959,  1.72437939,  1.73240071],
                        [ 4.62466435,  4.64282585,  4.64883546,  4.64209002,  4.62353373],
                        [ 1.13796576,  1.1332263 ,  1.13188339,  1.13355718,  1.13870903],
                        [-2.73897147, -2.7431784 , -2.74439527, -2.74292759, -2.73919646],
                        [ 5.33798009,  5.36671616,  5.37698092,  5.36664715,  5.33733776],
                        [-0.07983388, -0.08137769, -0.08198561, -0.08144084, -0.07990471],
                        [ 2.88060565,  2.87562323,  2.87428471,  2.87712677,  2.88359621]])
    
    # PH 10 weights
    weights = np.array([ 88626.92211908, -70709.65863336, -30231.349887, 56004.8990578, 
                        -1082.42491069, 5100.4311594, 51338.39360698, -54685.46124054,
                        -8899.94962529, 110627.99059007, -87522.96351739, 9066.58612171,
                        -46058.10449502, -62095.6044784, 40526.28457053])

    # # PH 40 centers   
    # centres = np.array([[ 1.13849724,  1.13360037,  1.13204758,  1.13361066,  1.13857987],
    #                     [ 4.63472636,  4.65310245,  4.65897865,  4.65232362,  4.63375888],
    #                     [-0.8986716 , -0.89937048, -0.89978866, -0.89980915, -0.89947921],
    #                     [-1.84517016, -1.84631476, -1.84667009, -1.84647502, -1.84547284],
    #                     [ 2.91579706,  2.91035033,  2.90818251,  2.90995219,  2.9150817 ],
    #                     [ 6.41995667,  6.45635485,  6.46887912,  6.45705329,  6.42132929],
    #                     [-0.12390447, -0.12542157, -0.12589472, -0.1253692 , -0.12378436],
    #                     [-4.33563786, -4.36422581, -4.37395983, -4.36421911, -4.33564394],
    #                     [ 1.75521588,  1.74649288,  1.74342831,  1.74643993,  1.7547182 ],
    #                     [-2.9514525 , -2.95562168, -2.9570375 , -2.95531506, -2.95084999],
    #                     [ 5.34202955,  5.37122377,  5.3818558 ,  5.37150663,  5.34199765],
    #                     [ 3.46416796,  3.46342102,  3.46299432,  3.462758  ,  3.46292406],
    #                     [ 4.02446471,  4.03287821,  4.0358944 ,  4.03367297,  4.02602676],
    #                     [ 2.35466714,  2.34502203,  2.34212622,  2.34584407,  2.35607495],
    #                     [ 0.50469454,  0.50122728,  0.49983583,  0.500838  ,  0.50406332]])
    
    # # PH 40 weights
    # weights = np.array([ -41224.50928588, 52866.22736494, 111069.22035209, -78232.82071587,
    #                      -65669.52077813, 5550.57042626, -956.14241484, -2703.01640318,
    #                       159711.88721709, 23325.41315535, -37412.52459471, -25895.04333611,
    #                       16613.12284684, -15115.84431373, -101922.77986793])

    # Initialize online K-means with 5 clusters
    online_kmeans = OnlineKMeans(n_clusters=num_centers, 
                                 adaptation_rate=adaptation_rate,
                                #  eta_0=0.9,
                                #  p=0.1,
                                #  momentum=0.05, 
                                 random_state=42,
                                 initial_centers=centres,)
    initial_centers = online_kmeans.initialise_centres(X_initial)
    # print(f'initial_centers: {initial_centers}')
    
    # Initialize and train the RBF network using QR decomposition
    rbf_net = RBFNetworkQR(num_centers=num_centers, 
                           centers=initial_centers,
                           regulariser=regulariser)
    rbf_net.fit(X_initial, y_initial)

    # print(f'Weights: {rbf_net.weights}')

    # Incrementally update the RBF network with the remaining data points
    y_pred = []
    # previous_error = 0
    for i in range(X_predict.shape[0]):
        updated_centers = online_kmeans.update(X_predict[i])
        last_split_cluster_idx = online_kmeans.last_split_cluster_idx
        rbf_net.update(X_update[i], 
                       y_update[i],
                       updated_centers,
                       max_num_measures,
                       last_split_cluster_idx)
        temp_pred = rbf_net.predict(X_predict[i].reshape(1, -1))[0]
        # temp_pred = temp_pred + 0.1*previous_error
        y_pred.append(temp_pred)
        # if i > prediction_horizon:
        #     previous_error = y_predict[i-prediction_horizon] - y_pred[-prediction_horizon]

    erros = np.abs(y_predict - y_pred)

    # save the error to a csv file
    erros_df = pd.DataFrame(erros, columns=['Error'])
    erros_df.to_csv(f'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error.csv', index=False)

    BenchmarkScore_U = math.sqrt(mean_squared_error(y_predict, y_pred))
    print('Benchmark_U Score: %.5f RMSE' % (BenchmarkScore_U))
    percentile = 95
    percentile_error = np.percentile(np.abs(y_predict - y_pred), percentile)
    print(f'Percentile Error: {percentile_error}')
    print(f'for window_size: {window_size} and num_centers: {num_centers} and adaptation_rate: {adaptation_rate} and regulariser: {regulariser} and max_num_measures: {max_num_measures}')

    # Generate implicit x-values
    t = np.arange(len(y_wind))

    # Plot the true time series and the 10th step ahead predictions
    plt.figure(figsize=(12, 6))
    plt.plot(t, y_wind, label='True Time Series', color='black', linewidth=4)
    plt.plot(t[10:], y_wind[0:-10], label='Persistence Method', color='blue', linestyle='--', linewidth=4)
    plt.plot(t[number_of_initial_points + 2*prediction_horizon + window_size:], y_pred, label='RBF NN Method', color='red', linestyle='--', linewidth=4)
    plt.title('10th Step Ahead Time Series Prediction using RBF NN (updating) VS Persistence', fontsize=32)
    plt.xlabel('Time Step', fontsize=23)
    plt.ylabel('Wind Speed (m/s)', fontsize=23)
    plt.legend(fontsize=20)
    plt.show()

    
    # for i in range(5,101,5):
    #     for j in range(5,101,5):
            # NN(file_name = 'raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_10',
            # window_size = 5,
            # num_centers = 15,
            # adaptation_rate = 0.0,
            # regulariser =0,
            # prediction_horizon = 10)

    # for i in range(5,101,5):
    #     for j in range(5,101,5):
    #         NN(file_name = 'raspberry/data/wind_data/16-09-23--18-50/16-09-23--18-50_N_10',
    #         window_size = j,
    #         num_centers = i,
    #         adaptation_rate = 0.0,
    #         regulariser =0,
    #         prediction_horizon = 10)

    # for i in range(5,101,5):
    #     for j in range(5,101,5):
    #         NN(file_name = 'raspberry/data/wind_data/25-09-23--17-06/25-09-23--17-06_N_10',
    #         window_size = j,
    #         num_centers = i,
    #         adaptation_rate = 0.0,
    #         regulariser =0,
    #         prediction_horizon = 10)


    #     # Parameters for training and testing
    # window_size = 5
    # prediction_horizon = 10
    # number_of_initial_points = 1000
    # num_centers = 15  # Number of RBF centers
    # adaptation_rate=0.  # Adaptation rate for online K-means
    # regulariser = 0 # Regularization parameter

    # # Read Data
    # df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[8])

    # series = df_wind.values.reshape(-1)

    # # Prepare the time series data for RBF network
    # X, y = prepare_time_series_data(prediction_direction='y',
    #                                 x_wind=series,
    #                                 y_wind=series,
    #                                 z_wind=series,
    #                                 window_size=window_size,
    #                                 prediction_horizon=prediction_horizon)

    # # Split the data: first number of initial points for initial fit, 
    # # rest for updates
    # # X_initial = X[:number_of_initial_points]
    # # y_initial = y[:number_of_initial_points]
    # # X_update = X[number_of_initial_points:]
    # # y_update = y[number_of_initial_points:]
    # # X_predict = X[number_of_initial_points + prediction_horizon:]
    # # y_predict = y[number_of_initial_points + prediction_horizon:]

    # # Initialize online K-means with 5 clusters
    # # online_kmeans = OnlineKMeans(n_clusters=num_centers, 
    # #                              adaptation_rate=adaptation_rate, 
    # #                              random_state=42)
    # # initial_centers = online_kmeans.initialise_centres(X_initial)

    # rbf_centers = np.array([[-0.2519472 , -0.25365488, -0.25430911, -0.25364477, -0.25179315],
    #                     [ 2.77295882,  2.76653372,  2.76491827,  2.76739702,  2.7745351 ],
    #                     [-2.3743145 , -2.37655631, -2.37690156, -2.3760605 , -2.37423063],
    #                     [ 6.15450014,  6.19011598,  6.20217724,  6.1895908 ,  6.1535908 ],
    #                     [-0.85281143, -0.85339148, -0.85360216, -0.85366156, -0.8531531 ],
    #                     [ 0.80346461,  0.79983013,  0.79848972,  0.79951519,  0.80288604],
    #                     [ 4.96727853,  4.99043908,  4.99910713,  4.99144907,  4.96811646],
    #                     [ 2.09594176,  2.08686475,  2.0833297 ,  2.08573047,  2.0939597 ],
    #                     [-1.56083405, -1.56121559, -1.56133649, -1.56123233, -1.56112372],
    #                     [ 0.21129298,  0.2090593 ,  0.20842501,  0.2092731 ,  0.21116801],
    #                     [ 3.45384033,  3.45303683,  3.45250379,  3.45288811,  3.45360119],
    #                     [-3.35251783, -3.36309745, -3.36661586, -3.36269548, -3.35123619],
    #                     [ 1.44229285,  1.43462734,  1.43227445,  1.4354158 ,  1.44364446],
    #                     [-4.72951996, -4.75980798, -4.77278209, -4.76375405, -4.73330744],
    #                     [ 4.15581724,  4.1665886 ,  4.1695666 ,  4.16562545,  4.15500131]])
    
    # rbf_U_weights = np.array([-3.29887501e+05, -1.62156967e+05,  1.48092107e+05,  8.49408567e+02,
    #                             6.92945904e+05,  1.04229416e+04, -1.26211186e+03, -3.35666129e+04,
    #                             -4.66305316e+05, -1.41340022e+05,  1.31829918e+05, -1.97102961e+04,
    #                             2.02703056e+05,  4.20506458e+02, -3.30368247e+04])
    
    # # Initialize and train the RBF network using QR decomposition
    # rbf_net = RBFNetworkQR(num_centers=num_centers, 
    #                        centers=rbf_centers,
    #                        regulariser=regulariser,
    #                         weights=rbf_U_weights)
    # # rbf_net.fit(X_initial, y_initial)

    # # Incrementally update the RBF network with the remaining data points
    # y_pred = []
    # for i in range(X.shape[0]):
    #     y_pred.append(rbf_net.predict(X[i].reshape(1, -1))[0])

    # BenchmarkScore_U = math.sqrt(mean_squared_error(y, y_pred))
    # print('Benchmark_U Score: %.5f RMSE' % (BenchmarkScore_U))
    # percentile = 95
    # percentile_error = np.percentile(np.abs(y - y_pred), percentile)
    # print(f'Percentile Error: {percentile_error}')

    # # Generate implicit x-values
    # t = np.arange(len(series))

    # # Plot the true time series and the 10th step ahead predictions
    # plt.figure(figsize=(12, 6))
    # plt.plot(t, series, label='True Time Series', color='black', linewidth=4)
    # plt.plot(t[prediction_horizon + window_size:], y_pred, label='10th Step Ahead Prediction', color='red', linestyle='--', linewidth=4)
    # plt.title('10th Step Ahead Time Series Prediction using RBF Neural Network', fontsize=32)
    # plt.xlabel('Time Step', fontsize=23)
    # plt.ylabel('Wind Speed (m/s)', fontsize=23)
    # plt.legend(fontsize=20)
    # plt.show()
    
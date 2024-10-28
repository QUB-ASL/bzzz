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
                 regulariser=None):
        """
        Initialize the RBF Network.

        :param num_centers: Number of RBF centers
        :param sigma: Width of RBF kernels
        :param centers: RBF centers (initialized later)
        :param regulariser: Regularization parameter
        """
        self.num_centers = num_centers
        self.sigma = sigma
        self.centers = centers
        self.regulariser = regulariser
        self.Q = None
        self.R = None
        self.weights = None
        self.b = None
        self.I = np.eye(num_centers)

    def _rbf_function(self, x, center):
        """
        Gaussian RBF function.

        :param x: Input vector
        :param center: Center of the RBF
        :return: RBF value
        """
        return np.exp(-np.linalg.norm(x - center) ** 2 / (2 * self.sigma ** 2))

    def _calculate_phi(self, X):
        """
        Calculate the design matrix Phi using the RBF function.

        :param X: Input data
        :return: Design matrix Phi
        """
        n_samples = X.shape[0]
        Phi = np.zeros((n_samples, self.num_centers))
        for i in range(n_samples):
            for j in range(self.num_centers):
                Phi[i, j] = self._rbf_function(X[i], self.centers[j])
        return Phi

    def fit(self, X, y):
        """
        Fit the RBF Network to the data.

        :param X: Input data
        :param y: Target values
        """
        # If sigma is not specified, calculate it based on the distances 
        # between centers
        if self.sigma is None:
            dists = np.linalg.norm(self.centers[:, np.newaxis] 
                                   - self.centers, axis=2)
            self.sigma = np.mean(dists)

        Phi = self._calculate_phi(X)
        # Solve for the weights using QR decomposition
        self.Q, self.R = np.linalg.qr(Phi.T @ Phi)
        self.b = Phi.T @ y
        rhs = self.Q.T @ self.b
        lhs = self.R + self.regulariser * self.I
        self.weights = spla.solve_triangular(lhs, rhs)

    def update(self, 
               new_X, 
               new_y, 
               updated_centers):
        """
        Update the RBF Network with a new sample.

        :param new_X: New input sample
        :param new_y: New target value
        :param updated_centers: Updated RBF centers
        """
        self.centers = updated_centers

        # Compute the RBF activation for the new sample new_X
        new_Phi = self._calculate_phi(new_X.reshape(1, -1))
        new_Phi = new_Phi.reshape(-1)

        self.Q, self.R = spla.qr_update(self.Q, self.R, new_Phi, new_Phi)

        self.b = self.b + new_y * new_Phi
        rhs = self.Q.T @ self.b
        lhs = self.R + self.regulariser * self.I
        self.weights = spla.solve_triangular(lhs, rhs)

    def predict(self, X):
        """
        Predict the output for new inputs.

        :param X: Input data
        :return: Predicted values
        """
        Phi = self._calculate_phi(X)
        return np.dot(Phi, self.weights)


def prepare_time_series_data(series, 
                             window_size, 
                             prediction_horizon):
    """
    Prepare time series data for training.

    :param series: Time series data
    :param window_size: Size of the window
    :param prediction_horizon: Prediction horizon
    :return: Prepared input and target data
    """
    X, y = [], []
    for i in range(len(series) - window_size - prediction_horizon + 1):
        X.append(series[i:i + window_size])
        y.append(series[i + window_size + prediction_horizon - 1])
    return np.array(X), np.array(y)


def predict_tenth_step_ahead(model, 
                             series, 
                             window_size, 
                             prediction_horizon):
    """
    Predict the tenth step ahead in a time series.

    :param model: Trained RBF Network model
    :param series: Time series data
    :param window_size: Size of the window
    :param prediction_horizon: Prediction horizon
    :return: Predicted values
    """
    n_predictions = len(series) - window_size - prediction_horizon + 1
    predictions = []
    for i in range(n_predictions):
        input_seq = series[i:i + window_size]
        prediction = recursive_prediction(model, input_seq, steps_ahead=prediction_horizon)
        predictions.append(prediction[-1])
    return np.array(predictions)


def recursive_prediction(model, 
                         input_seq, 
                         steps_ahead):
    """
    Perform recursive prediction for multi-step ahead forecasting.

    :param model: Trained RBF Network model
    :param input_seq: Input sequence
    :param steps_ahead: Number of steps ahead to predict
    :return: Predicted sequence
    """
    prediction = input_seq.copy()
    for _ in range(steps_ahead):
        next_input = prediction[-model.centers.shape[1]:].reshape(1, -1)
        next_pred = model.predict(next_input)
        prediction = np.append(prediction, next_pred)
    return prediction[-steps_ahead:]


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

    t = pd.read_csv(f'{file_name}.csv', usecols=[0])
    t = t.values.reshape(-1)
    
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
                                 forgetting_factor=None, 
                                 random_state=42)
    # Determine the centers for U, V, and W components
    U_centers = online_kmeans.initialize_centers(X_U)
    V_centers = online_kmeans.initialize_centers(X_V)
    W_centers = online_kmeans.initialize_centers(X_W)

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

    y_pred_U = predict_tenth_step_ahead(rbf_net_U, 
                                        series_U, 
                                        window_size, 
                                        prediction_horizon)
    y_pred_V = predict_tenth_step_ahead(rbf_net_V, 
                                        series_V, 
                                        window_size, 
                                        prediction_horizon)
    y_pred_W = predict_tenth_step_ahead(rbf_net_W, 
                                        series_W, 
                                        window_size, 
                                        prediction_horizon)

    trainScore_U = math.sqrt(mean_squared_error(y_U, y_pred_U))
    print('Benchmark_U Score: %.5f RMSE' % (trainScore_U))
    trainScore_V = math.sqrt(mean_squared_error(y_V, y_pred_V))
    print('Benchmark_V Score: %.5f RMSE' % (trainScore_V))
    trainScore_W = math.sqrt(mean_squared_error(y_W, y_pred_W))
    print('Benchmark_W Score: %.5f RMSE' % (trainScore_W))

    with open(f'{file_name}_PH_{prediction_horizon}_RMSE_U.csv',
              "a+", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([f'Train_U_Window_size_{window_size}_Number_of_centers_{num_centers}', trainScore_U])

    with open(f'{file_name}_PH_{prediction_horizon}_RMSE_V.csv',
              "a+", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([f'Train_V_Window_size_{window_size}_Number_of_centers_{num_centers}', trainScore_V])

    with open(f'{file_name}_PH_{prediction_horizon}_RMSE_W.csv',
              "a+", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([f'Train_W_Window_size_{window_size}_Number_of_centers_{num_centers}', trainScore_W])

# Example usage
if __name__ == "__main__":

    # # Parameters for training and testing
    # window_size = 15
    # prediction_horizon = 10
    # number_of_initial_points = 500
    # num_centers = 5  # Number of RBF centers
    # adaptation_rate=0.1  # Adaptation rate for online K-means
    # regulariser = 0  # Regularization parameter

    # # Read Data
    # df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[3])

    # series = df_wind.values.reshape(-1)

    # t = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[0])
    # t = t.values.reshape(-1)
    
    # # Prepare the time series data for RBF network
    # X, y = prepare_time_series_data(series, window_size, prediction_horizon)

    # # Split the data: first number of initial points for initial fit, 
    # # rest for updates
    # X_initial = X[:number_of_initial_points]
    # y_initial = y[:number_of_initial_points]
    # X_remaining = X[number_of_initial_points:]
    # y_remaining = y[number_of_initial_points:]

    # # Initialize online K-means with 5 clusters
    # online_kmeans = OnlineKMeans(n_clusters=num_centers, 
    #                              adaptation_rate=adaptation_rate, 
    #                              forgetting_factor=None, 
    #                              random_state=42)
    # initial_centers = online_kmeans.initialize_centers(X_initial)
    
    # # Initialize and train the RBF network using QR decomposition
    # rbf_net = RBFNetworkQR(num_centers=num_centers, 
    #                        centers=initial_centers,
    #                        regulariser=regulariser)
    # rbf_net.fit(X_initial, y_initial)

    # # Incrementally update the RBF network with the remaining data points
    # for i in range(X_remaining.shape[0]):
    #     updated_centers = online_kmeans.update(i)
    #     rbf_net.update(X_remaining[i], 
    #                    y_remaining[i],
    #                    updated_centers)
    
    # # Predict the 10th step ahead for the entire series
    # y_pred = predict_tenth_step_ahead(rbf_net, 
    #                                   series, 
    #                                   window_size, 
    #                                   prediction_horizon)
    
    # BenchmarkScore_U = math.sqrt(mean_squared_error(y, y_pred))
    # print('Benchmark_U Score: %.5f RMSE' % (BenchmarkScore_U))

    # # Plot the true time series and the 10th step ahead predictions
    # plt.figure(figsize=(12, 6))
    # plt.plot(t, series, label='True Time Series', color='blue')
    # plt.plot(t[window_size + prediction_horizon - 1:], y_pred, label='10th Step Ahead Prediction', color='red', linestyle='--')
    # plt.title('10th Step Ahead Time Series Prediction using RBF Neural Network (QR Decomposition)')
    # plt.xlabel('Time')
    # plt.ylabel('Value')
    # plt.legend()
    # plt.show()

    
    for i in range(5,101,5):
        for j in range(i,101,5):
            NN(file_name = 'raspberry/data/wind_data/25-09-23--16-49/25-09-23--16-49_N_10',
            window_size = j,
            num_centers = i,
            adaptation_rate = 0.1,
            regulariser =0,
            prediction_horizon = 10)
    
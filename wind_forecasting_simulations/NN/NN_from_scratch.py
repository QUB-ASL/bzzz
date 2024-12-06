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
        self.X = None
        self.y = None
        self.A = None

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
        # If sigma is not specified, calculate it based on the distances 
        # between centers
        if self.sigma is None:
            dists = np.linalg.norm(self.centers[:, np.newaxis] 
                                   - self.centers, axis=2)
            self.sigma = np.mean(dists)

        A = self._calculate_A(X)
        # Solve for the weights using QR decomposition
        self.Q, self.R = np.linalg.qr(A.T @ A)
        self.b = A.T @ y
        rhs = self.Q.T @ self.b
        lhs = self.R + self.regulariser * self.I
        self.weights = spla.solve_triangular(lhs, rhs)
        self.X = X
        self.y = y
        self.A = A

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

        # Check if the number of centers has changed
        if len(updated_centers) != self.num_centers:
            # Update the number of centers
            self.num_centers = len(updated_centers)
            self.I = np.eye(self.num_centers)
            self.centers = updated_centers

            # Append a new column and row to Q and R for the new center
            a = np.zeros((self.X.shape[0], 1))
            for i in range(self.X.shape[0]):
                 a[i] = self._rbf_function(self.X[1], updated_centers[-1])
            new_column = self.A.T @ a
            self.A = np.hstack((self.A, a))
            new_row = a.T @ self.A

            self.Q, self.R = spla.qr_insert(self.Q, self.R, new_column, self.num_centers - 1, 'col')
            self.Q, self.R = spla.qr_insert(self.Q, self.R, new_row, self.num_centers - 1, 'row')
            new_b = a.T @ self.y
            self.b = np.append(self.b, new_b)
            print(new_X, new_y)

        else:
            self.centers = updated_centers

        # Compute the RBF activation for the new sample new_X
        new_A = self._calculate_A(new_X.reshape(1, -1))
        new_A = new_A.reshape(-1)

        # Update the QR decomposition using rank-1 update
        self.Q, self.R = spla.qr_update(self.Q, self.R, new_A, new_A)

        # Update the b vector
        self.b = self.b + new_y * new_A

        # Solve for updated weights
        rhs = self.Q.T @ self.b
        lhs = self.R + self.regulariser * self.I
        self.weights = spla.solve_triangular(lhs, rhs)

        # Append lists
        self.X = np.vstack((self.X, new_X))
        self.y = np.append(self.y, new_y)
        self.A = np.vstack((self.A, new_A))

    def predict(self, X):
        """
        Predict the output for new inputs.

        :param X: Input data
        :return: Predicted values
        """
        A = self._calculate_A(X)
        return np.dot(A, self.weights)


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
    for i in range(len(series) - window_size - prediction_horizon):
        X.append(series[i+window_size:i:-1])
        y.append(series[i + window_size + prediction_horizon])
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
                                 forgetting_factor=None, 
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

    with open(f'{file_name}_RBF_NN_PH_{prediction_horizon}_RMSE_U.csv',
              "a+", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([f'Train_U_Window_size_{window_size}_Number_of_centers_{num_centers}', trainScore_U])

    with open(f'{file_name}_RBF_NN_PH_{prediction_horizon}_RMSE_V.csv',
              "a+", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([f'Train_V_Window_size_{window_size}_Number_of_centers_{num_centers}', trainScore_V])

    with open(f'{file_name}_RBF_NN_PH_{prediction_horizon}_RMSE_W.csv',
              "a+", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([f'Train_W_Window_size_{window_size}_Number_of_centers_{num_centers}', trainScore_W])

# Example usage
if __name__ == "__main__":

    # Parameters for training and testing
    window_size = 15
    prediction_horizon = 10
    number_of_initial_points = 1000
    num_centers = 5  # Number of RBF centers
    adaptation_rate=0.  # Adaptation rate for online K-means
    regulariser = 0. # Regularization parameter

    # Read Data
    df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[8])

    series = df_wind.values.reshape(-1)

    # Prepare the time series data for RBF network
    X, y = prepare_time_series_data(series, window_size, prediction_horizon)

    # Split the data: first number of initial points for initial fit, 
    # rest for updates
    X_initial = X[:number_of_initial_points]
    y_initial = y[:number_of_initial_points]
    X_update = X[number_of_initial_points:]
    y_update = y[number_of_initial_points:]
    X_predict = X[number_of_initial_points + prediction_horizon:]
    y_predict = y[number_of_initial_points + prediction_horizon:]

    # Initialize online K-means with 5 clusters
    online_kmeans = OnlineKMeans(n_clusters=num_centers, 
                                 adaptation_rate=adaptation_rate, 
                                 random_state=42)
    initial_centers = online_kmeans.initialise_centres(X_initial)
    
    # Initialize and train the RBF network using QR decomposition
    rbf_net = RBFNetworkQR(num_centers=num_centers, 
                           centers=initial_centers,
                           regulariser=regulariser)
    rbf_net.fit(X_initial, y_initial)

    # Incrementally update the RBF network with the remaining data points
    y_pred = []
    for i in range(X_predict.shape[0]):
        updated_centers = online_kmeans.update(X_predict[i])
        rbf_net.update(X_update[i], 
                       y_update[i],
                       updated_centers)
        y_pred.append(rbf_net.predict(X_predict[i].reshape(1, -1))[0])

    BenchmarkScore_U = math.sqrt(mean_squared_error(y_predict, y_pred))
    print('Benchmark_U Score: %.5f RMSE' % (BenchmarkScore_U))

    # Generate implicit x-values
    t = np.arange(len(series))

    # Plot the true time series and the 10th step ahead predictions
    plt.figure(figsize=(12, 6))
    plt.plot(t, series, label='True Time Series', color='blue')
    plt.plot(t[number_of_initial_points + 2*prediction_horizon + window_size:], y_pred, label='10th Step Ahead Prediction', color='red', linestyle='--')
    plt.title('10th Step Ahead Time Series Prediction using RBF Neural Network (QR Decomposition)')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.show()

    
    # for i in range(5,101,5):
    #     for j in range(5,101,5):
    #         NN(file_name = 'raspberry/data/wind_data/25-09-23--17-06/25-09-23--17-06_N_10',
    #         window_size = j,
    #         num_centers = i,
    #         adaptation_rate = 0.0,
    #         regulariser =0,
    #         prediction_horizon = 10)
    
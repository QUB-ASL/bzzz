########## RBF NN QR decomposition to solve the 
########## least squares problem with rank-1 update 

# Standard library imports
import math
import csv
import pickle as pk

# Third-party imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.linalg as spla
import seaborn as sns
from sklearn.metrics import mean_squared_error
from sklearn.decomposition import PCA

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
                 a[i] = self._rbf_function(self.X[i], updated_centers[-1])
            new_column = self.A.T @ a
            self.A = np.hstack((self.A, a))
            new_row = a.T @ self.A

            self.Q, self.R = spla.qr_insert(self.Q, self.R, new_column, self.num_centers - 1, 'col')
            self.Q, self.R = spla.qr_insert(self.Q, self.R, new_row, self.num_centers - 1, 'row')
            new_b = a.T @ self.y
            self.b = np.append(self.b, new_b)

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
        lhs = self.R
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

class PCA_for_RBF:
    """
    Principal Component Analysis.
    """
    def __init__(self, 
                 n_components,
                 Load_params=False):
        """
        Initialize the PCA.

        :param n_components: Number of principal components
        """
        self.PCA = PCA(n_components=n_components)
        if Load_params == True:
            self.PCA = pk.load(open('PCA.pkl', 'rb'))

    def fit(self, X):
        """
        Fit the PCA to the data.

        :param X: Input data
        """
        self.PCA.fit(X)
        pk.dump(self.PCA, open('PCA.pkl', 'wb'))
        

    def transform(self, X):
        """
        Transform the data using the fitted PCA.

        :param X: Input data
        :return: Transformed data
        """
        return self.PCA.transform(X)

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
    adaptation_rate= 0.00 # Adaptation rate for online K-means
    regulariser = 0.00001 # Regularization parameter

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
    
    PCA_X = PCA_for_RBF(n_components=2,
                        Load_params=True)
    # PCA_X.fit(X)
    X = PCA_X.transform(X)
    print('here')

    # Split the data: first number of initial points for initial fit, 
    # rest for updates
    X_initial = X[:number_of_initial_points]
    y_initial = y[:number_of_initial_points]
    X_update = X[number_of_initial_points:]
    y_update = y[number_of_initial_points:]
    X_predict = X[number_of_initial_points + prediction_horizon:]
    y_predict = y[number_of_initial_points + prediction_horizon:]

    # centres = np.array([[-0.2519472 , -0.25365488, -0.25430911, -0.25364477, -0.25179315],
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
    
    # centres = np.array([[-0.26369844, -0.2667903 , -0.26927166, -0.27111328, -0.27210503,  1.05201925,  1.05293297,  1.05466732,  1.0573009 ,  1.06059682,  0.11081136,  0.10859501, 0.10801303,  0.10913464,  0.11196048],
    #                     [ 0.44889693,  0.44643974,  0.45172766,  0.46470193,  0.48484132,  3.84755611,  3.87081744,  3.88852109,  3.90024689,  3.90535969,  0.18197384,  0.1828456 , 0.18450593,  0.18680872,  0.18955854],
    #                     [ 1.65804164,  1.655854  ,  1.65492456,  1.65482809,  1.6553669 ,  3.13329682,  3.13003828,  3.12953227,  3.13163651,  3.13566313,  0.20224211,  0.19853286, 0.19775135,  0.19971148,  0.20428734],
    #                     [-1.53590489, -1.54459817, -1.54876631, -1.54829825, -1.54348653,  1.17217134,  1.17696196,  1.17941072,  1.17949583,  1.17765093,  0.33963357,  0.34045182, 0.34026507,  0.33909914,  0.33689739],
    #                     [-0.39202976, -0.38893874, -0.38893245, -0.39212747, -0.39845614, -1.72764796, -1.7247154 , -1.72165033, -1.71874732, -1.71619821,  0.06046015,  0.05748692, 0.05662407,  0.05792556,  0.06139292],
    #                     [ 2.75312453,  2.75765179,  2.75682235,  2.75070225,  2.74009945,  4.01458842,  4.00980952,  4.00106647,  3.98865954,  3.97410026,  0.3497249 ,  0.34841195, 0.34800981,  0.34904205,  0.35138015],
    #                     [-0.76872034, -0.76981029, -0.769946  , -0.76902265, -0.76718511, -0.22953888, -0.23034131, -0.23021995, -0.22920289, -0.22722161,  0.31826304,  0.31957068, 0.3204332 ,  0.32061294,  0.32016777],
    #                     [ 0.48404392,  0.48662735,  0.48680697,  0.4844751 ,  0.47974823,  0.0566357 ,  0.05232512,  0.04997337,  0.04969417,  0.05145641,  0.31321472,  0.3133579 , 0.31273094,  0.3113613 ,  0.30933921],
    #                     [ 1.75145746,  1.76491832,  1.77863739,  1.79183829,  1.80402953,  4.78655066,  4.81677747,  4.83318685,  4.83425843,  4.81997157,  0.39907399,  0.40339313, 0.40590976,  0.40607816,  0.40392678],
    #                     [-0.95919353, -0.95589204, -0.95034897, -0.94247014, -0.93253446, -3.47808729, -3.49115391, -3.49592152, -3.49178082, -3.47916233,  0.09138706,  0.0907745 , 0.09054996,  0.09067573,  0.0912343 ],
    #                     [ 2.53968121,  2.53727436,  2.53217891,  2.52509308,  2.5163437 ,  2.43823428,  2.40767264,  2.3888497 ,  2.38336388,  2.39089756,  0.63608649,  0.64376098, 0.6463648 ,  0.64382479,  0.63622624],
    #                     [-1.8424748 , -1.85150959, -1.85607738, -1.85597115, -1.85118513, -1.27800611, -1.28395503, -1.28917716, -1.29372018, -1.29778161,  0.48189513,  0.48477329, 0.4850896 ,  0.48313321,  0.47885508],
    #                     [ 0.05067594,  0.04459247,  0.04201303,  0.0431838 ,  0.04810074,  2.3818313 ,  2.39230389,  2.40151334,  2.40878837,  2.41434712,  0.07608585,  0.07353051, 0.07217563,  0.07245066,  0.0742802 ],
    #                     [ 3.31314632,  3.33503938,  3.34797443,  3.35160883,  3.34564313,  5.54370561,  5.56325254,  5.5641193 ,  5.5464381 ,  5.51056771,  0.44830137,  0.45200567, 0.45457774,  0.45598126,  0.45640628],
    #                     [ 1.32107234,  1.31169028,  1.3033641 ,  1.29663548,  1.29158871,  1.62748613,  1.60937287,  1.60245164,  1.60724983,  1.62362588,  0.35747043,  0.35665478, 0.35419345,  0.35003767,  0.34432142]])

    # centres = np.array([[-1.19891957, -1.20119565, -1.2011672 , -1.19938767, -1.1960682 ,  0.38941678,  0.38799123,  0.38632627,  0.38488823,  0.38371534],
    #                     [ 1.88154983,  1.89409469,  1.9061348 ,  1.91699349,  1.92599837,  4.70371786,  4.73035299,  4.74389057,  4.74262173,  4.72671269],
    #                     [-1.01824706, -1.01536395, -1.00987541, -1.00155767, -0.99074158, -3.47736337, -3.49117851, -3.49699692, -3.49409282, -3.48239168],
    #                     [ 0.49945239,  0.49144955,  0.48764106,  0.4882011 ,  0.49304384,  2.54504658,  2.55187533,  2.56028506,  2.57032303,  2.58159947],
    #                     [-1.66033043, -1.66881624, -1.67374156, -1.6748766 , -1.67225767, -1.08223517, -1.08633913, -1.08988312, -1.09304629, -1.09596841],
    #                     [ 1.72969734,  1.72071016,  1.71188343,  1.70365502,  1.6960984 ,  1.85813389,  1.83332797,  1.8218133 ,  1.82415898,  1.83976709],
    #                     [-0.39344552, -0.39015062, -0.39016763, -0.39341651, -0.39952132, -1.81357095, -1.81042589, -1.80667063, -1.80277009, -1.79913993],
    #                     [ 1.9420661 ,  1.94055605,  1.93890999,  1.93697107,  1.9350365 ,  3.1485714 ,  3.13873534,  3.13216963,  3.12949409,  3.13114887],
    #                     [ 3.28960995,  3.3112692 ,  3.32433284,  3.32802988,  3.32240813,  5.581866  ,  5.60303705,  5.60539797,  5.58855901,  5.55321885],
    #                     [ 2.9591365 ,  2.96466219,  2.96385598,  2.9569512 ,  2.94442286,  3.93986747,  3.93249492,  3.92261763,  3.91048342,  3.89674688],
    #                     [-1.4649214 , -1.47562789, -1.48023934, -1.47777731, -1.46870471,  2.03967562,  2.05602798,  2.06674201,  2.07054885,  2.06829085],
    #                     [-0.30789871, -0.30845616, -0.308887  , -0.30914484, -0.30910769, -0.24532182, -0.24613054, -0.24559927, -0.24360695, -0.24023725],
    #                     [ 0.7449737 ,  0.74769599,  0.74789943,  0.74544098,  0.74012181,  0.28178859,  0.27478636,  0.27099777,  0.27040089,  0.27280101],
    #                     [ 0.62542968,  0.62627341,  0.63359316,  0.64758194,  0.66753252,  3.92679845,  3.9503251 ,  3.96786203,  3.97909403,  3.98342393],
    #                     [-0.17592425, -0.17945324, -0.18244187, -0.18472499, -0.18599687,  1.26726499,  1.26909373,  1.2712802 ,  1.27394088,  1.27696198]])

    centres = np.array([[-2.25680872e+00,  6.09914383e-04],
                        [ 5.55017437e+00, -4.19243140e-04],
                        [-9.58718811e+00, -8.91219225e-04],
                        [ 1.84552229e+00,  9.45025121e-05],
                        [-5.23438328e+00,  1.19196584e-04],
                        [ 8.50572868e+00, -2.97831391e-03],
                        [ 3.09502492e+00,  2.53980193e-03],
                        [ 5.17201914e-01, -9.93246229e-04],
                        [-1.27303909e+01, -2.78819517e-04],
                        [ 1.08790913e+01,  8.50900588e-04],
                        [-3.68946993e+00, -2.17275578e-04],
                        [ 4.30921083e+00, -1.29527278e-03],
                        [ 6.91422769e+00,  1.67428674e-03],
                        [-7.18394989e+00,  5.25851495e-04],
                        [-8.39792693e-01, -4.11009805e-04]])

    # Initialize online K-means with 5 clusters
    online_kmeans = OnlineKMeans(n_clusters=num_centers, 
                                 adaptation_rate=adaptation_rate,
                                #  eta_0=0.9,
                                #  p=0.1,
                                #  momentum=0.5, 
                                 random_state=42,
                                 initial_centers=centres)
    initial_centers = online_kmeans.initialise_centres(X_initial)
    # print(f'initial_centers: {initial_centers}')
    
    # Initialize and train the RBF network using QR decomposition
    rbf_net = RBFNetworkQR(num_centers=num_centers, 
                           centers=initial_centers,
                           regulariser=regulariser)
    rbf_net.fit(X_initial, y_initial)

    # Incrementally update the RBF network with the remaining data points
    y_pred = []
    # previous_error = 0
    for i in range(X_predict.shape[0]):
        updated_centers = online_kmeans.update(X_predict[i])
        rbf_net.update(X_update[i], 
                       y_update[i],
                       updated_centers)
        temp_pred = rbf_net.predict(X_predict[i].reshape(1, -1))[0]
        # temp_pred = temp_pred + 0.1*previous_error
        y_pred.append(temp_pred)
        # if i > prediction_horizon:
        #     previous_error = y_predict[i-prediction_horizon] - y_pred[-prediction_horizon]

    BenchmarkScore_U = math.sqrt(mean_squared_error(y_predict, y_pred))
    print('Benchmark_U Score: %.5f RMSE' % (BenchmarkScore_U))
    percentile = 95
    percentile_error = np.percentile(np.abs(y_predict - y_pred), percentile)
    print(f'Percentile Error: {percentile_error}')
    print(f'for window_size: {window_size} and num_centers: {num_centers} and adaptation_rate: {adaptation_rate} and regulariser: {regulariser}')

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
    
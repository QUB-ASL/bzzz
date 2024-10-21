import numpy as np
import scipy as sp
import scipy.linalg as spla

n_samples = 1000
n_features = 20

A = np.random.randn(n_samples, n_features)
y = np.random.randn(n_samples, 1)

Q, R = np.linalg.qr(A.T @ A)
b = A.T @ y
rhs = Q.T @ b
x_star = spla.solve_triangular(R, rhs)

# Test
x_star_true = np.linalg.lstsq(A, y)[0]
print(x_star_true)
err = x_star- x_star_true
print(f"Error: {np.linalg.norm(err, np.inf)}")




x_new = np.random.randn(n_features, 1)
y_new = 0.1

import time

start = time.time()
for i in range(10000):
    Qnew, Rnew = spla.qr_update(Q, R, x_new, x_new)
    rhs_updated = b + y_new * x_new
    x_star_updated = spla.solve_triangular(Rnew, Qnew.T @ rhs_updated)
end = time.time()
print((end - start)/10000)

# print(x_star)
# print(x_star_updated)

# Test
A_big = np.vstack((A, x_new.T))
y_big = np.vstack((y, y_new))

errQRupdate = Qnew @ Rnew - A_big.T @ A_big
errRhsNew = rhs_updated - (A_big.T @ y_big)
# print(errRhsNew)
x_star_updated_true = np.linalg.lstsq(A_big, y_big, rcond=1e-6)[0]

err_updated = x_star_updated_true - x_star_updated
# print(err_updated)








######################################################
###############################################################
######################################################














import numpy as np
import scipy as sp
import scipy.linalg as spla

n_samples = 1000
n_features = 20

A = np.random.randn(n_samples, n_features)
y = np.random.randn(n_samples, 1)

Q, R = np.linalg.qr(A)
rhs = Q.T @ y
x_star = spla.solve_triangular(R, rhs)

# # Test
# x_star_true = np.linalg.lstsq(A, y)[0]
# print(x_star_true)
# err = x_star- x_star_true
# print(f"Error: {np.linalg.norm(err, np.inf)}")




x_new = np.random.randn(1, n_features)
y_new = 0.1

# Create u and v vectors for qr_update
u = np.zeros(Q.shape[0] + 1)  # u has the same number of rows as Q, plus one extra for the new row
u[-1] = 1  # Adding the effect of the new row at the bottom

v = x_new  # v is the new row to be added

import time

start = time.time()
for i in range(10000):
    Qnew, Rnew = spla.qr_update(Q, R, u, v)
    # y_update = np.vstack((y, y_new))
    # rhs_updated = Qnew.T @ y_update
    # x_star_updated = spla.solve_triangular(Rnew, rhs_updated)
end = time.time()
print((end - start)/10000)

# print(x_star)
# print(x_star_updated)

# # Test
# A_big = np.vstack((A, x_new))
# y_big = np.vstack((y, y_new))

# errQRupdate = Qnew @ Rnew - A_big.T @ A_big
# errRhsNew = rhs_updated - (A_big.T @ y_big)
# print(errRhsNew)
# x_star_updated_true = np.linalg.lstsq(A_big, y_big, rcond=1e-6)[0]

# err_updated = x_star_updated_true - x_star_updated
# print(err_updated)












########## RBF NN QR decomposition to solve the least squares problem #####################

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import scipy.linalg as spla

# Function to perform QR decomposition to solve the least squares problem
def qr_solve(A, y):
    # Compute the QR decomposition of A^T A
    Q, R = np.linalg.qr(A.T @ A)
    b = A.T @ y
    rhs = Q.T @ b
    x_star = spla.solve_triangular(R, rhs)
    return x_star

class RBFNetworkQR:
    def __init__(self, num_centers, sigma=None):
        self.num_centers = num_centers
        self.sigma = sigma
        self.centers = None
        self.weights = None

    def _rbf_function(self, x, center):
        # Gaussian RBF
        return np.exp(-np.linalg.norm(x - center)**2 / (2 * self.sigma**2))
    
    def _calculate_phi(self, X):
        # Calculate the design matrix Phi using the RBF function
        n_samples = X.shape[0]
        Phi = np.zeros((n_samples, self.num_centers))
        for i in range(n_samples):
            for j in range(self.num_centers):
                Phi[i, j] = self._rbf_function(X[i], self.centers[j])
        return Phi

    def fit(self, X, y):
        # Use KMeans to select the centers for the RBFs
        kmeans = KMeans(n_clusters=self.num_centers, random_state=42).fit(X)
        self.centers = kmeans.cluster_centers_
        
        # If sigma is not specified, calculate it based on the distances between centers
        if self.sigma is None:
            dists = np.linalg.norm(self.centers[:, np.newaxis] - self.centers, axis=2)
            self.sigma = np.mean(dists)
        
        # Compute the design matrix Phi
        Phi = self._calculate_phi(X)
        
        # Solve for the weights using QR decomposition
        self.weights = qr_solve(Phi, y)

    def predict(self, X):
        # Compute the design matrix Phi for new inputs
        Phi = self._calculate_phi(X)
        return np.dot(Phi, self.weights)

# Time series data preparation function
def prepare_time_series_data(series, window_size, prediction_horizon):
    X, y = [], []
    for i in range(len(series) - window_size - prediction_horizon + 1):
        X.append(series[i:i + window_size])
        y.append(series[i + window_size + prediction_horizon - 1])
    return np.array(X), np.array(y)

# Prediction function for time series (multi-step prediction)
def predict_tenth_step_ahead(model, series, window_size, prediction_horizon):
    n_predictions = len(series) - window_size - prediction_horizon + 1
    predictions = []
    for i in range(n_predictions):
        input_seq = series[i:i + window_size]
        prediction = recursive_prediction(model, input_seq, steps_ahead=prediction_horizon)
        predictions.append(prediction[-1])
    return np.array(predictions)

def recursive_prediction(model, input_seq, steps_ahead):
    prediction = input_seq.copy()
    for _ in range(steps_ahead):
        next_input = prediction[-model.centers.shape[1]:].reshape(1, -1)
        next_pred = model.predict(next_input)
        prediction = np.append(prediction, next_pred)
    return prediction[-steps_ahead:]

# Example usage
if __name__ == "__main__":
    # Generate synthetic time series data (e.g., sine wave with noise)
    # t = np.linspace(0, 20, 200)
    # series = np.sin(t) + np.random.normal(0, 0.1, t.shape)
    # # print(t)
    # print(series)


    # Read Data
    df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[3])

    series = df_wind.values.reshape(-1)
    # print(series)

    t = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[0])
    t = t.values.reshape(-1)
    # print(t)
    
    # Prepare the time series data for RBF network
    window_size = 100
    prediction_horizon = 10
    X, y = prepare_time_series_data(series, window_size, prediction_horizon)
    
    # Define RBF network parameters
    num_centers = 50  # Number of RBF centers
    sigma = 10.0  # RBF sigma
    
    # Initialize and train the RBF network using QR decomposition
    rbf_net = RBFNetworkQR(num_centers=num_centers)
    rbf_net.fit(X, y)
    
    # Predict the 10th step ahead for the entire series
    y_pred = predict_tenth_step_ahead(rbf_net, series, window_size, prediction_horizon)
    
    # Plot the true time series and the 10th step ahead predictions
    plt.figure(figsize=(12, 6))
    plt.plot(t, series, label='True Time Series', color='blue')
    plt.plot(t[window_size + prediction_horizon - 1:], y_pred, label='10th Step Ahead Prediction', color='red', linestyle='--')
    plt.title('10th Step Ahead Time Series Prediction using RBF Neural Network (QR Decomposition)')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.show()














################################################################################################################################################








# ########## RBF NN Cholesky decomposition to solve the least squares problem with Cholesky rank-1 update function #####################

# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.cluster import KMeans
# from scipy.linalg import cho_solve, cho_factor, cholesky, solve_triangular

# # Function to perform Cholesky decomposition and solve the least squares problem
# def cholesky_solve(L, A_T_b):
#     # Solve L * y = A_T_b
#     y = solve_triangular(L, A_T_b, lower=True)
#     # Solve L^T * x = y
#     x = solve_triangular(L.T, y, lower=False)
#     return x

# class RBFNetworkCholesky:
#     def __init__(self, num_centers, sigma=None):
#         self.num_centers = num_centers
#         self.sigma = sigma
#         self.centers = None
#         self.weights = None
#         self.L = None  # Cholesky factor of A^T A
#         self.A_T_b = None  # A^T * b, the projection of the target vector

#     def _rbf_function(self, x, center):
#         # Gaussian RBF
#         return np.exp(-np.linalg.norm(x - center) ** 2 / (2 * self.sigma ** 2))

#     def _calculate_phi(self, X):
#         # Calculate the design matrix Phi using the RBF function
#         n_samples = X.shape[0]
#         Phi = np.zeros((n_samples, self.num_centers))
#         for i in range(n_samples):
#             for j in range(self.num_centers):
#                 Phi[i, j] = self._rbf_function(X[i], self.centers[j])
#         return Phi

#     def fit(self, X, y):
#         # Use KMeans to select the centers for the RBFs
#         kmeans = KMeans(n_clusters=self.num_centers, random_state=42).fit(X)
#         self.centers = kmeans.cluster_centers_

#         # If sigma is not specified, calculate it based on the distances between centers
#         if self.sigma is None:
#             dists = np.linalg.norm(self.centers[:, np.newaxis] - self.centers, axis=2)
#             self.sigma = np.mean(dists)

#         # Compute the design matrix Phi
#         Phi = self._calculate_phi(X)

#         # Compute the Gram matrix A^T A and the vector A^T b
#         A_T_A = np.dot(Phi.T, Phi)
#         A_T_b = np.dot(Phi.T, y)

#         # Perform Cholesky decomposition of A^T A
#         self.L = cholesky(A_T_A, lower=True)
#         self.A_T_b = A_T_b

#         # Solve for the initial weights using Cholesky decomposition
#         self.weights = cholesky_solve(self.L, self.A_T_b)

#     def update(self, X_new, y_new):
#         # Compute the new row in Phi corresponding to X_new
#         Phi_new_row = self._calculate_phi(X_new.reshape(1, -1)).flatten()

#         # Update the Gram matrix A^T A with the new row
#         A_T_A_new_row = np.outer(Phi_new_row, Phi_new_row)
#         self.L = cholesky_update(self.L, Phi_new_row)

#         # Update the projection A^T b with the new target value
#         A_T_b_new = np.dot(Phi_new_row, y_new)
#         self.A_T_b += A_T_b_new

#         # Solve the updated system
#         self.weights = cholesky_solve(self.L, self.A_T_b)

#     def predict(self, X):
#         # Compute the design matrix Phi for new inputs
#         Phi = self._calculate_phi(X)
#         return np.dot(Phi, self.weights)

# # Cholesky rank-1 update function
# def cholesky_update(L, x):
#     """
#     Update the Cholesky factor L of a matrix A^T A after adding a new row x to the matrix A.
#     This performs a rank-1 update.
#     """
#     for i in range(len(x)):
#         r = np.sqrt(L[i, i] ** 2 + x[i] ** 2)
#         c = r / L[i, i]
#         s = x[i] / L[i, i]
#         L[i, i] = r
#         if i + 1 < len(x):
#             L[i + 1:, i] = (L[i + 1:, i] + s * x[i + 1:]) / c
#             x[i + 1:] = c * x[i + 1:] - s * L[i + 1:, i]
#     return L

# # Time series data preparation function
# def prepare_time_series_data(series, window_size, prediction_horizon):
#     X, y = [], []
#     for i in range(len(series) - window_size - prediction_horizon + 1):
#         X.append(series[i:i + window_size])
#         y.append(series[i + window_size + prediction_horizon - 1])
#     return np.array(X), np.array(y)

# # Prediction function for time series (multi-step prediction)
# def predict_tenth_step_ahead(model, series, window_size, prediction_horizon):
#     n_predictions = len(series) - window_size - prediction_horizon + 1
#     predictions = []
#     for i in range(n_predictions):
#         input_seq = series[i:i + window_size]
#         prediction = recursive_prediction(model, input_seq, steps_ahead=prediction_horizon)
#         predictions.append(prediction[-1])
#     return np.array(predictions)

# def recursive_prediction(model, input_seq, steps_ahead):
#     prediction = input_seq.copy()
#     for _ in range(steps_ahead):
#         next_input = prediction[-model.centers.shape[1]:].reshape(1, -1)
#         next_pred = model.predict(next_input)
#         prediction = np.append(prediction, next_pred)
#     return prediction[-steps_ahead:]

# # Example usage
# if __name__ == "__main__":
#     # Read Data
#     df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[3])
#     series = df_wind.values.reshape(-1)

#     t = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[0])
#     t = t.values.reshape(-1)

#     # Prepare the time series data for RBF network
#     window_size = 100
#     prediction_horizon = 10
#     X, y = prepare_time_series_data(series, window_size, prediction_horizon)

#     # Define RBF network parameters
#     num_centers = 20  # Number of RBF centers
#     sigma = 10.0  # RBF sigma

#     # Initialize and train the RBF network using Cholesky decomposition
#     rbf_net = RBFNetworkCholesky(num_centers=num_centers)
#     rbf_net.fit(X, y)

#     # Predict the 10th step ahead for the entire series
#     y_pred = predict_tenth_step_ahead(rbf_net, series, window_size, prediction_horizon)

#     # Plot the true time series and the 10th step ahead predictions
#     plt.figure(figsize=(12, 6))
#     plt.plot(t, series, label='True Time Series', color='blue')
#     plt.plot(t[window_size + prediction_horizon - 1:], y_pred, label='10th Step Ahead Prediction', color='red', linestyle='--')
#     plt.title('10th Step Ahead Time Series Prediction using RBF Neural Network (Cholesky Decomposition)')
#     plt.xlabel('Time')
#     plt.ylabel('Value')
#     plt.legend()
#     plt.show()


# # Update with new data (example with the next row of data)
#     X_new = X[-1, :]  # Example new input
#     y_new = y[-1]     # Corresponding new target value
#     rbf_net.update(X_new, y_new)  # Perform the rank-1 update

















################################################################################################################################################








# ########## RBF NN QR decomposition to solve the regularised least squares problem #####################

# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.cluster import KMeans

# # Function to perform QR decomposition to solve the regularised least squares problem
# def qr_solve_regularised(A, b, reg_lambda):
#     """
#     Solves the regularised least squares problem (ridge regression) using QR decomposition.
#     Solves (A.T @ A + lambda * I) x = A.T @ b
#     """
#     n_features = A.shape[1]
#     # Regularise the design matrix (A.T @ A + lambda * I)
#     A_reg = np.vstack([A, np.sqrt(reg_lambda) * np.eye(n_features)])
#     b_reg = np.vstack([b, np.zeros((n_features, 1))])
    
#     # QR decomposition of the regularised matrix
#     Q, R = np.linalg.qr(A_reg)
    
#     # Solve R * x = Q.T * b
#     Q_T_b = np.dot(Q.T, b_reg)
#     x = np.linalg.solve(R, Q_T_b[:n_features])
    
#     return x

# class RBFNetworkQR:
#     def __init__(self, num_centres, sigma=None, reg_lambda=1e-2):
#         self.num_centres = num_centres  # Number of RBF centres
#         self.sigma = sigma              # Width of RBF kernels
#         self.reg_lambda = reg_lambda    # Regularisation parameter (lambda)
#         self.centres = None             # RBF centres (initialised later)
#         self.weights = None             # Weights (learned through training)

#     def _rbf_function(self, x, centre):
#         # Gaussian RBF
#         return np.exp(-np.linalg.norm(x - centre)**2 / (2 * self.sigma**2))
    
#     def _calculate_phi(self, X):
#         # Calculate the design matrix Phi using the RBF function
#         n_samples = X.shape[0]
#         Phi = np.zeros((n_samples, self.num_centres))
#         for i in range(n_samples):
#             for j in range(self.num_centres):
#                 Phi[i, j] = self._rbf_function(X[i], self.centres[j])
#         return Phi

#     def fit(self, X, y):
#         # Use KMeans to select the centres for the RBFs
#         kmeans = KMeans(n_clusters=self.num_centres, random_state=42).fit(X)
#         self.centres = kmeans.cluster_centers_
        
#         # If sigma is not specified, calculate it based on the distances between centres
#         if self.sigma is None:
#             dists = np.linalg.norm(self.centres[:, np.newaxis] - self.centres, axis=2)
#             self.sigma = np.mean(dists)
        
#         # Compute the design matrix Phi
#         Phi = self._calculate_phi(X)
        
#         # Solve for the weights using regularised QR decomposition
#         self.weights = qr_solve_regularised(Phi, y, self.reg_lambda)

#     def predict(self, X):
#         # Compute the design matrix Phi for new inputs
#         Phi = self._calculate_phi(X)
#         return np.dot(Phi, self.weights)

# # Time series data preparation function
# def prepare_time_series_data(series, window_size, prediction_horizon):
#     X, y = [], []
#     for i in range(len(series) - window_size - prediction_horizon + 1):
#         X.append(series[i:i + window_size])
#         y.append(series[i + window_size + prediction_horizon - 1])
#     return np.array(X), np.array(y)

# # Prediction function for time series (multi-step prediction)
# def predict_tenth_step_ahead(model, series, window_size, prediction_horizon):
#     n_predictions = len(series) - window_size - prediction_horizon + 1
#     predictions = []
#     for i in range(n_predictions):
#         input_seq = series[i:i + window_size]
#         prediction = recursive_prediction(model, input_seq, steps_ahead=prediction_horizon)
#         predictions.append(prediction[-1])
#     return np.array(predictions)

# def recursive_prediction(model, input_seq, steps_ahead):
#     prediction = input_seq.copy()
#     for _ in range(steps_ahead):
#         next_input = prediction[-model.centres.shape[1]:].reshape(1, -1)
#         next_pred = model.predict(next_input)
#         prediction = np.append(prediction, next_pred)
#     return prediction[-steps_ahead:]

# # Example usage
# if __name__ == "__main__":
#     # Generate synthetic time series data (e.g., sine wave with noise)
#     # t = np.linspace(0, 20, 200)
#     # series = np.sin(t) + np.random.normal(0, 0.1, t.shape)

#     # Read Data
#     df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[3])

#     series = df_wind.values.reshape(-1)
#     # print(series)

#     t = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[0])
#     t = t.values.reshape(-1)
#     # print(t)
    
#     # Prepare the time series data for RBF network
#     window_size = 120
#     prediction_horizon = 10
#     X, y = prepare_time_series_data(series, window_size, prediction_horizon)
#     y = y.reshape(-1, 1)  # Reshape y for compatibility with QR solve
    
#     # Define RBF network parameters
#     num_centres = 10    # Number of RBF centres
#     sigma = 1.0         # RBF sigma
#     reg_lambda = 0.01   # Regularisation strength
    
#     # Initialise and train the RBF network using regularised QR decomposition
#     rbf_net = RBFNetworkQR(num_centres=num_centres, reg_lambda=reg_lambda)
#     rbf_net.fit(X, y)
    
#     # Predict the 10th step ahead for the entire series
#     y_pred = predict_tenth_step_ahead(rbf_net, series, window_size, prediction_horizon)
    
#     # Plot the true time series and the 10th step ahead predictions
#     plt.figure(figsize=(12, 6))
#     plt.plot(t, series, label='True Time Series', color='blue')
#     plt.plot(t[window_size + prediction_horizon - 1:], y_pred, label='10th Step Ahead Prediction', color='red', linestyle='--')
#     plt.title('10th Step Ahead Time Series Prediction using RBF Neural Network (Regularised QR Decomposition)')
#     plt.xlabel('Time')
#     plt.ylabel('Value')
#     plt.legend()
#     plt.show()






















###############################################################################################################################
#################################################################################################################################

























# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.cluster import KMeans

# # Function to perform QR decomposition to solve the regularised least squares problem
# def qr_solve_regularised(A, b, reg_lambda):
#     """
#     Solves the regularised least squares problem (ridge regression) using QR decomposition.
#     Solves (A.T @ A + lambda * I) x = A.T @ b
#     """
#     n_features = A.shape[1]
#     # Regularise the design matrix (A.T @ A + lambda * I)
#     A_reg = np.vstack([A, np.sqrt(reg_lambda) * np.eye(n_features)])
#     b_reg = np.vstack([b, np.zeros((n_features, 1))])
    
#     # QR decomposition of the regularised matrix
#     Q, R = np.linalg.qr(A_reg)
    
#     # Solve R * x = Q.T * b
#     Q_T_b = np.dot(Q.T, b_reg)
#     x = np.linalg.solve(R, Q_T_b[:n_features])
    
#     return x

# def qr_rank1_update(Q, R, x):
#     """
#     Perform a QR rank-1 update when a new sample x is available.
#     This updates the QR decomposition (Q, R) of the existing data matrix
#     to incorporate the new sample x without recomputing the whole QR decomposition.
#     """
#     x = x.reshape(-1, 1)  # Ensure x is a column vector (n_samples, 1)
    
#     # Project x onto the subspace spanned by Q
#     x_proj = Q.T @ x  # Projection of x onto Q
    
#     # Compute the residual (the part of x orthogonal to Q)
#     r_new = x - Q @ x_proj
#     r_norm = np.linalg.norm(r_new)
    
#     # If r_new is non-zero, normalize and update Q and R
#     if r_norm > 1e-10:  # Ensure we have a significant new component
#         r_new /= r_norm  # Normalize residual

#         # Update R by appending the projection and the norm as new row/column
#         R = np.vstack([R, x_proj.T])  # Add x_proj as a new row to R
#         R = np.hstack([R, np.vstack([np.zeros(R.shape[0] - 1), r_norm])])  # Add r_norm as a new column to R

#         # Update Q by adding r_new as a new column
#         Q = np.hstack([Q, r_new])  # Append the new basis vector to Q
    
#     return Q, R

# def cholesky_rank1_update(L, x):
#     """
#     Perform a rank-1 update of the Cholesky factor L with vector x (add x x^T).
#     """
#     x = x.reshape(-1, 1)  # Ensure x is a column vector
#     n = L.shape[0]
#     x = x.flatten()
#     L_new = L.copy()
#     for k in range(n):
#         r = np.hypot(L_new[k, k], x[k])
#         c = r / L_new[k, k]
#         s = x[k] / L_new[k, k]
#         L_new[k, k] = r
#         if k < n - 1:
#             L_new[k + 1:n, k] = (L_new[k + 1:n, k] + s * x[k + 1:n]) / c
#             x[k + 1:n] = c * x[k + 1:n] - s * L_new[k + 1:n, k]
#     return L_new

# class RBFNetworkQR:
#     def __init__(self, num_centres, sigma=None, reg_lambda=1e-2):
#         self.num_centres = num_centres  # Number of RBF centres
#         self.sigma = sigma              # Width of RBF kernels
#         self.reg_lambda = reg_lambda    # Regularisation parameter (lambda)
#         self.centres = None             # RBF centres (initialised later)
#         self.Q = None                   # Q matrix from QR decomposition
#         self.R = None                   # R matrix from QR decomposition
#         self.weights = None             # Weights (learned through training)

#     def _rbf_function(self, x, centre):
#         # Gaussian RBF
#         return np.exp(-np.linalg.norm(x - centre)**2 / (2 * self.sigma**2))
    
#     def _calculate_phi(self, X):
#         # Calculate the design matrix Phi using the RBF function
#         n_samples = X.shape[0]
#         Phi = np.zeros((n_samples, self.num_centres))
#         for i in range(n_samples):
#             for j in range(self.num_centres):
#                 Phi[i, j] = self._rbf_function(X[i], self.centres[j])
#         return Phi

#     def fit(self, X, y):
#         # Use KMeans to select the centres for the RBFs
#         kmeans = KMeans(n_clusters=self.num_centres, random_state=42).fit(X)
#         self.centres = kmeans.cluster_centers_
        
#         # If sigma is not specified, calculate it based on the distances between centres
#         if self.sigma is None:
#             dists = np.linalg.norm(self.centres[:, np.newaxis] - self.centres, axis=2)
#             self.sigma = np.mean(dists)

#         # Compute the design matrix Phi
#         Phi = self._calculate_phi(X)
        
#         # Solve for the weights using regularised QR decomposition
#         self.weights = qr_solve_regularised(Phi, y, self.reg_lambda)

#     def update(self, new_X, new_y):
#         """
#         Update the model when new data (new_X, new_y) arrives using QR rank-1 update.
#         """
#         # Compute the RBF activation for the new sample new_X
#         new_Phi = self._calculate_phi(new_X)
        
#         for i in range(new_Phi.shape[0]):
#             phi_new = new_Phi[i, :].reshape(-1, 1)
#             self.Q, self.R = qr_rank1_update(self.Q, self.R, phi_new)
        
#         # Update weights using the updated R matrix
#         self.weights = np.linalg.solve(self.R.T, np.dot(self.Q.T, new_y))

#     def predict(self, X):
#         # Compute the design matrix Phi for new inputs
#         Phi = self._calculate_phi(X)
#         return np.dot(Phi, self.weights)

# class RBFNetworkCholesky:
#     def __init__(self, num_centres, sigma=None, reg_lambda=1e-2):
#         self.num_centres = num_centres  # Number of RBF centres
#         self.sigma = sigma              # Width of RBF kernels
#         self.reg_lambda = reg_lambda    # Regularisation parameter (lambda)
#         self.centres = None             # RBF centres (initialised later)
#         self.Phi_T_Phi = None           # Phi.T @ Phi
#         self.Phi_T_y = None             # Phi.T @ y
#         self.L = None                   # Cholesky factor of Phi.T @ Phi
#         self.weights = None             # Weights (learned through training)

#     def _rbf_function(self, x, centre):
#         # Gaussian RBF
#         return np.exp(-np.linalg.norm(x - centre)**2 / (2 * self.sigma**2))
    
#     def _calculate_phi(self, X):
#         # Calculate the design matrix Phi using the RBF function
#         n_samples = X.shape[0]
#         Phi = np.zeros((n_samples, self.num_centres))
#         for i in range(n_samples):
#             for j in range(self.num_centres):
#                 Phi[i, j] = self._rbf_function(X[i], self.centres[j])
#         return Phi

#     def fit(self, X, y):
#         # Use KMeans to select the centres for the RBFs
#         kmeans = KMeans(n_clusters=self.num_centres, random_state=42).fit(X)
#         self.centres = kmeans.cluster_centers_
        
#         # If sigma is not specified, calculate it based on the distances between centres
#         if self.sigma is None:
#             dists = np.linalg.norm(self.centres[:, np.newaxis] - self.centres, axis=2)
#             self.sigma = np.mean(dists)
        
#         # Initialize Phi_T_Phi and Phi_T_y
#         self.Phi_T_Phi = self.reg_lambda * np.eye(self.num_centres)
#         self.Phi_T_y = np.zeros((self.num_centres, 1))
#         self.L = np.linalg.cholesky(self.Phi_T_Phi)
        
#         # Compute the design matrix Phi
#         Phi = self._calculate_phi(X)
        
#         # Update Phi_T_Phi, Phi_T_y and perform Cholesky rank-1 update
#         for i in range(Phi.shape[0]):
#             phi_i = Phi[i, :].reshape(-1, 1)
#             self.L = cholesky_rank1_update(self.L, phi_i)
#             self.Phi_T_Phi += phi_i @ phi_i.T
#             self.Phi_T_y += phi_i * y[i]

#         # Solve the linear system for weights
#         self.weights = np.linalg.solve(self.L.T, np.linalg.solve(self.L, self.Phi_T_y))

#     def update(self, new_X, new_y):
#         """
#         Update the model when new data (new_X, new_y) arrives using Cholesky rank-1 update.
#         """
#         # Compute the RBF activation for the new sample new_X
#         new_Phi = self._calculate_phi(new_X)
        
#         for i in range(new_Phi.shape[0]):
#             phi_new = new_Phi[i, :].reshape(-1, 1)
#             self.L = cholesky_rank1_update(self.L, phi_new)
#             self.Phi_T_Phi += phi_new @ phi_new.T
#             self.Phi_T_y += phi_new * new_y[i]

#         # Update weights using the updated Cholesky factor
#         self.weights = np.linalg.solve(self.L.T, np.linalg.solve(self.L, self.Phi_T_y))

#     def predict(self, X):
#         # Compute the design matrix Phi for new inputs
#         Phi = self._calculate_phi(X)
#         return np.dot(Phi, self.weights)

# # Time series data preparation function
# def prepare_time_series_data(series, window_size, prediction_horizon):
#     X, y = [], []
#     for i in range(len(series) - window_size - prediction_horizon + 1):
#         X.append(series[i:i + window_size])
#         y.append(series[i + window_size + prediction_horizon - 1])
#     return np.array(X), np.array(y)

# # Prediction function for time series (multi-step prediction)
# def predict_tenth_step_ahead(model, series, window_size, prediction_horizon):
#     n_predictions = len(series) - window_size - prediction_horizon + 1
#     predictions = []
#     for i in range(n_predictions):
#         input_seq = series[i:i + window_size]
#         prediction = recursive_prediction(model, input_seq, steps_ahead=prediction_horizon)
#         predictions.append(prediction[-1])
#     return np.array(predictions)

# def recursive_prediction(model, input_seq, steps_ahead):
#     prediction = input_seq.copy()
#     for _ in range(steps_ahead):
#         next_input = prediction[-model.centres.shape[1]:].reshape(1, -1)
#         next_pred = model.predict(next_input)
#         prediction = np.append(prediction, next_pred)
#     return prediction[-steps_ahead:]

# # Example usage with first 50 points for fitting and remaining for incremental updates
# if __name__ == "__main__":
#     # Generate synthetic time series data (e.g., sine wave with noise)
#     t = np.linspace(0, 20, 200)
#     series = np.sin(t) + np.random.normal(0, 0.1, t.shape)
    
#     # Prepare the time series data for RBF network
#     window_size = 50
#     prediction_horizon = 10
#     X, y = prepare_time_series_data(series, window_size, prediction_horizon)
#     y = y.reshape(-1, 1)  # Reshape y for compatibility with QR solve
    
#     # Split the data: first 50 points for initial fit, rest for updates
#     X_initial = X[:50]
#     y_initial = y[:50]
#     X_remaining = X[50:]
#     y_remaining = y[50:]
    
#     # Define RBF network parameters
#     num_centres = 10    # Number of RBF centres
#     sigma = 1.0         # RBF sigma
#     reg_lambda = 0.01   # Regularisation strength
    
#     # Initialise and train the RBF network using regularised QR decomposition on the first 50 points
#     rbf_net_qr = RBFNetworkQR(num_centres=num_centres, reg_lambda=reg_lambda)
#     rbf_net_qr.fit(X_initial, y_initial)
    
#     # Incrementally update the RBF network with the remaining data points
#     for i in range(X_remaining.shape[0]):
#         rbf_net_qr.update(X_remaining[i].reshape(1, -1), y_remaining[i].reshape(1, -1))
    
#     # Predict the 10th step ahead for the entire series using QR update
#     y_pred_qr = predict_tenth_step_ahead(rbf_net_qr, series, window_size, prediction_horizon)
    
#     # Initialise and train the RBF network using Cholesky decomposition on the first 50 points
#     rbf_net_chol = RBFNetworkCholesky(num_centres=num_centres, reg_lambda=reg_lambda)
#     rbf_net_chol.fit(X_initial, y_initial)
    
#     # Incrementally update the RBF network with the remaining data points
#     for i in range(X_remaining.shape[0]):
#         rbf_net_chol.update(X_remaining[i].reshape(1, -1), y_remaining[i].reshape(1, -1))
    
#     # Predict the 10th step ahead for the entire series using Cholesky update
#     y_pred_chol = predict_tenth_step_ahead(rbf_net_chol, series, window_size, prediction_horizon)
    
#     # Plot the true time series and the 10th step ahead predictions
#     plt.figure(figsize=(12, 6))
#     plt.plot(t, series, label='True Time Series', color='blue')
#     plt.plot(t[window_size + prediction_horizon - 1:], y_pred_qr, label='QR 10th Step Ahead Prediction', color='red')
#     plt.plot(t[window_size + prediction_horizon - 1:], y_pred_chol, label='Cholesky 10th Step Ahead Prediction', color='green', linestyle='--')
#     plt.title('10th Step Ahead Time Series Prediction using RBF Neural Network')
#     plt.xlabel('Time')
#     plt.ylabel('Value')
#     plt.legend()
#     plt.show()












######################################################################
#####################################################################












# import numpy as np 
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.cluster import KMeans

# # Function to perform QR decomposition to solve the regularised least squares problem
# def qr_solve_regularised(A, b, reg_lambda):
#     """
#     Solves the regularised least squares problem (ridge regression) using QR decomposition.
#     Solves (A.T @ A + lambda * I) x = A.T @ b
#     """
#     n_features = A.shape[1]
#     # Regularise the design matrix (A.T @ A + lambda * I)
#     A_reg = np.vstack([A, np.sqrt(reg_lambda) * np.eye(n_features)])
#     b_reg = np.vstack([b, np.zeros((n_features, 1))])
    
#     # QR decomposition of the regularised matrix
#     Q, R = np.linalg.qr(A_reg)
    
#     # Solve R * x = Q.T * b
#     Q_T_b = np.dot(Q.T, b_reg)
#     x = np.linalg.solve(R, Q_T_b[:n_features])
    
#     return x

# def qr_rank1_update(Q, R, x):
#     """
#     Perform a QR rank-1 update when a new sample x is available.
#     This updates the QR decomposition (Q, R) of the existing data matrix
#     to incorporate the new sample x without recomputing the whole QR decomposition.
#     """
#     x = x.reshape(-1, 1)  # Ensure x is a column vector (n_samples, 1)
    
#     # Project x onto the subspace spanned by Q
#     x_proj = Q.T @ x  # Projection of x onto Q
    
#     # Compute the residual (the part of x orthogonal to Q)
#     r_new = x - Q @ x_proj
#     r_norm = np.linalg.norm(r_new)
    
#     # If r_new is non-zero, normalize and update Q and R
#     if r_norm > 1e-10:  # Ensure we have a significant new component
#         r_new /= r_norm  # Normalize residual

#         # Update R by appending the projection and the norm as new row/column
#         R = np.vstack([R, x_proj.T])  # Add x_proj as a new row to R
#         R = np.hstack([R, np.vstack([np.zeros(R.shape[0] - 1), r_norm])])  # Add r_norm as a new column to R

#         # Update Q by adding r_new as a new column
#         Q = np.hstack([Q, r_new])  # Append the new basis vector to Q
    
#     return Q, R

# def cholesky_rank1_update(L, x):
#     """
#     Perform a rank-1 update of the Cholesky factor L with vector x (add x x^T).
#     """
#     x = x.reshape(-1, 1)  # Ensure x is a column vector
#     n = L.shape[0]
#     x = x.flatten()
#     L_new = L.copy()
#     for k in range(n):
#         r = np.hypot(L_new[k, k], x[k])
#         c = r / L_new[k, k]
#         s = x[k] / L_new[k, k]
#         L_new[k, k] = r
#         if k < n - 1:
#             L_new[k + 1:n, k] = (L_new[k + 1:n, k] + s * x[k + 1:n]) / c
#             x[k + 1:n] = c * x[k + 1:n] - s * L_new[k + 1:n, k]
#     return L_new

# class RBFNetworkQR:
#     def __init__(self, num_centres, sigma=None, reg_lambda=1e-2):
#         self.num_centres = num_centres  # Number of RBF centres
#         self.sigma = sigma              # Width of RBF kernels
#         self.reg_lambda = reg_lambda    # Regularisation parameter (lambda)
#         self.centres = None             # RBF centres (initialised later)
#         self.Q = None                   # Q matrix from QR decomposition
#         self.R = None                   # R matrix from QR decomposition
#         self.weights = None             # Weights (learned through training)

#     def _rbf_function(self, x, centre):
#         # Gaussian RBF
#         return np.exp(-np.linalg.norm(x - centre)**2 / (2 * self.sigma**2))
    
#     def _calculate_phi(self, X):
#         # Calculate the design matrix Phi using the RBF function
#         n_samples = X.shape[0]
#         Phi = np.zeros((n_samples, self.num_centres))
#         for i in range(n_samples):
#             for j in range(self.num_centres):
#                 Phi[i, j] = self._rbf_function(X[i], self.centres[j])
#         return Phi

#     def fit(self, X, y):
#         # Use KMeans to select the centres for the RBFs
#         kmeans = KMeans(n_clusters=self.num_centres, random_state=42).fit(X)
#         self.centres = kmeans.cluster_centers_
        
#         # If sigma is not specified, calculate it based on the distances between centres
#         if self.sigma is None:
#             dists = np.linalg.norm(self.centres[:, np.newaxis] - self.centres, axis=2)
#             self.sigma = np.mean(dists)

#         # Compute the design matrix Phi
#         Phi = self._calculate_phi(X)
        
#         # Solve for the weights using regularised QR decomposition
#         self.weights = qr_solve_regularised(Phi, y, self.reg_lambda)

#     def update(self, new_X, new_y):
#         """
#         Update the model when new data (new_X, new_y) arrives using QR rank-1 update.
#         """
#         # Compute the RBF activation for the new sample new_X
#         new_Phi = self._calculate_phi(new_X)
        
#         for i in range(new_Phi.shape[0]):
#             phi_new = new_Phi[i, :].reshape(-1, 1)
#             self.Q, self.R = qr_rank1_update(self.Q, self.R, phi_new)
        
#         # Update weights using the updated R matrix
#         self.weights = np.linalg.solve(self.R.T, np.dot(self.Q.T, new_y))

#     def predict(self, X):
#         # Compute the design matrix Phi for new inputs
#         Phi = self._calculate_phi(X)
#         return np.dot(Phi, self.weights)

# class RBFNetworkCholesky:
#     def __init__(self, num_centres, sigma=None, reg_lambda=1e-2):
#         self.num_centres = num_centres  # Number of RBF centres
#         self.sigma = sigma              # Width of RBF kernels
#         self.reg_lambda = reg_lambda    # Regularisation parameter (lambda)
#         self.centres = None             # RBF centres (initialised later)
#         self.Phi_T_Phi = None           # Phi.T @ Phi
#         self.Phi_T_y = None             # Phi.T @ y
#         self.L = None                   # Cholesky factor of Phi.T @ Phi
#         self.weights = None             # Weights (learned through training)

#     def _rbf_function(self, x, centre):
#         # Gaussian RBF
#         return np.exp(-np.linalg.norm(x - centre)**2 / (2 * self.sigma**2))
    
#     def _calculate_phi(self, X):
#         # Calculate the design matrix Phi using the RBF function
#         n_samples = X.shape[0]
#         Phi = np.zeros((n_samples, self.num_centres))
#         for i in range(n_samples):
#             for j in range(self.num_centres):
#                 Phi[i, j] = self._rbf_function(X[i], self.centres[j])
#         return Phi

#     def fit(self, X, y):
#         # Use KMeans to select the centres for the RBFs
#         kmeans = KMeans(n_clusters=self.num_centres, random_state=42).fit(X)
#         self.centres = kmeans.cluster_centers_
        
#         # If sigma is not specified, calculate it based on the distances between centres
#         if self.sigma is None:
#             dists = np.linalg.norm(self.centres[:, np.newaxis] - self.centres, axis=2)
#             self.sigma = np.mean(dists)
        
#         # Initialize Phi_T_Phi and Phi_T_y
#         self.Phi_T_Phi = self.reg_lambda * np.eye(self.num_centres)
#         self.Phi_T_y = np.zeros((self.num_centres, 1))
#         self.L = np.linalg.cholesky(self.Phi_T_Phi)
        
#         # Compute the design matrix Phi
#         Phi = self._calculate_phi(X)
        
#         # Update Phi_T_Phi, Phi_T_y and perform Cholesky rank-1 update
#         for i in range(Phi.shape[0]):
#             phi_i = Phi[i, :].reshape(-1, 1)
#             self.L = cholesky_rank1_update(self.L, phi_i)
#             self.Phi_T_Phi += phi_i @ phi_i.T
#             self.Phi_T_y += phi_i * y[i]

#         # Solve the linear system for weights
#         self.weights = np.linalg.solve(self.L.T, np.linalg.solve(self.L, self.Phi_T_y))

#     def update(self, new_X, new_y):
#         """
#         Update the model when new data (new_X, new_y) arrives using Cholesky rank-1 update.
#         """
#         # Compute the RBF activation for the new sample new_X
#         new_Phi = self._calculate_phi(new_X)
        
#         for i in range(new_Phi.shape[0]):
#             phi_new = new_Phi[i, :].reshape(-1, 1)
#             self.L = cholesky_rank1_update(self.L, phi_new)
#             self.Phi_T_Phi += phi_new @ phi_new.T
#             self.Phi_T_y += phi_new @ new_y[i]

#         # Update weights using the updated Cholesky factor
#         self.weights = np.linalg.solve(self.L.T, np.linalg.solve(self.L, self.Phi_T_y))

#     def predict(self, X):
#         # Compute the design matrix Phi for new inputs
#         Phi = self._calculate_phi(X)
#         return np.dot(Phi, self.weights)

# # Time series data preparation function
# def prepare_time_series_data(series, window_size, prediction_horizon):
#     X, y = [], []
#     for i in range(len(series) - window_size - prediction_horizon + 1):
#         X.append(series[i:i + window_size])
#         y.append(series[i + window_size + prediction_horizon - 1])
#     return np.array(X), np.array(y)

# # Prediction function for time series (multi-step prediction)
# def predict_tenth_step_ahead(model, series, window_size, prediction_horizon):
#     n_predictions = len(series) - window_size - prediction_horizon + 1
#     predictions = []
#     for i in range(n_predictions):
#         input_seq = series[i:i + window_size]
#         prediction = recursive_prediction(model, input_seq, steps_ahead=prediction_horizon)
#         predictions.append(prediction[-1])
#     return np.array(predictions)

# def recursive_prediction(model, input_seq, steps_ahead):
#     prediction = input_seq.copy()
#     for _ in range(steps_ahead):
#         next_input = prediction[-model.centres.shape[1]:].reshape(1, -1)
#         next_pred = model.predict(next_input)
#         prediction = np.append(prediction, next_pred)
#     return prediction[-steps_ahead:]

# # Example usage
# if __name__ == "__main__":
#     # Generate synthetic time series data (e.g., sine wave with noise)
#     t = np.linspace(0, 20, 200)
#     series = np.sin(t) + np.random.normal(0, 0.1, t.shape)
    
#     # Prepare the time series data for RBF network
#     window_size = 50
#     prediction_horizon = 10
#     X, y = prepare_time_series_data(series, window_size, prediction_horizon)
#     y = y.reshape(-1, 1)  # Reshape y for compatibility with QR solve
    
#     # Define RBF network parameters
#     num_centres = 10    # Number of RBF centres
#     sigma = 1.0         # RBF sigma
#     reg_lambda = 0.01   # Regularisation strength
    
#     # Initialise and train the RBF network using regularised QR decomposition
#     rbf_net_qr = RBFNetworkQR(num_centres=num_centres, reg_lambda=reg_lambda)
#     rbf_net_qr.fit(X, y)
    
#     # Predict the 10th step ahead for the entire series using QR update
#     y_pred_qr = predict_tenth_step_ahead(rbf_net_qr, series, window_size, prediction_horizon)
    
#     # Initialise and train the RBF network using Cholesky decomposition
#     rbf_net_chol = RBFNetworkCholesky(num_centres=num_centres, reg_lambda=reg_lambda)
#     rbf_net_chol.fit(X, y)
    
#     # Predict the 10th step ahead for the entire series using Cholesky update
#     y_pred_chol = predict_tenth_step_ahead(rbf_net_chol, series, window_size, prediction_horizon)
    
#     # Plot the true time series and the 10th step ahead predictions
#     plt.figure(figsize=(12, 6))
#     plt.plot(t, series, label='True Time Series', color='blue')
#     plt.plot(t[window_size + prediction_horizon - 1:], y_pred_qr, label='QR 10th Step Ahead Prediction', color='red')
#     plt.plot(t[window_size + prediction_horizon - 1:], y_pred_chol, label='Cholesky 10th Step Ahead Prediction', color='green', linestyle='--')
#     plt.title('10th Step Ahead Time Series Prediction using RBF Neural Network')
#     plt.xlabel('Time')
#     plt.ylabel('Value')
#     plt.legend()
#     plt.show()
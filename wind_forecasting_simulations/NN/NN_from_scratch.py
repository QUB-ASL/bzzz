# import numpy as np
# import nnfs
# from nnfs.datasets import spiral_data

# nnfs.init()

# # Dense layer
# class Layer_Dense:

#     # Layer initialization
#     def __init__(self, n_inputs, n_neurons):

#         # Initialize weights and biases
#         self.weights = 0.01 * np.random.randn(n_inputs, n_neurons)
#         self.biases = np.zeros((1, n_neurons))

#     # Forward pass
#     def forward(self, inputs):
#         # Calculate output values from inputs, weights and biases
#         self.output = np.dot(inputs, self.weights) + self.biases

# # ReLU activation
# class Activation_ReLU:

#     # Forward pass
#     def forward(self, inputs):
#         # Calculate output values from inputs
#         self.output = np.maximum(0, inputs)

# # Softmax activation
# class Activation_Softmax:

#     # Forward pass
#     def forward(self, inputs):
        
#         # Get unnormalized probabilities
#         exp_values = np.exp(inputs - np.max(inputs, axis=1,
#         keepdims=True))

#         # Normalize them for each sample
#         probabilities = exp_values / np.sum(exp_values, axis=1,
#         keepdims=True)

#         self.output = probabilities

# # Common loss class
# class Loss:

#     # Calculates the data and regularization losses
#     # given model output and ground truth values
#     def calculate(self, output, y):

#         # Calculate sample losses
#         sample_losses = self.forward(output, y)

#         # Calculate mean loss
#         data_loss = np.mean(sample_losses)

#         # Return loss
#         return data_loss
    
# # Cross-entropy loss
# class Loss_CategoricalCrossentropy(Loss):

#     # Forward pass
#     def forward(self, y_pred, y_true):

#         # Number of samples in a batch
#         samples = len(y_pred)
        
#         # Clip data to prevent division by 0
#         # Clip both sides to not drag mean towards any value
#         y_pred_clipped = np.clip(y_pred, 1e-7, 1 - 1e-7)

#         # Probabilities for target values -
#         # only if categorical labels
#         if len(y_true.shape) == 1:
#             correct_confidences = y_pred_clipped[
#                 range(samples), y_true
#                 ]
            
#         # Mask values - only for one-hot encoded labels
#         elif len(y_true.shape) == 2:
#             correct_confidences = np.sum(
#             y_pred_clipped * y_true, axis=1
#             )

#         # Losses
#         negative_log_likelihoods = -np.log(correct_confidences)
#         return negative_log_likelihoods

# # Create dataset
# X, y = spiral_data(samples=100, classes=3)

# # Create Dense layer with 2 input features and 3 output values
# dense1 = Layer_Dense(2, 3)

# # Create ReLU activation (to be used with Dense layer):
# activation1 = Activation_Softmax()

# # # Create second Dense layer with 3 input features (as we take output
# # # of previous layer here) and 3 output values (output values)
# # dense2 = Layer_Dense(3, 3)

# # # Create Softmax activation (to be used with Dense layer):
# # activation2 = Activation_Softmax()

# # Create loss function
# loss_function = Loss_CategoricalCrossentropy()

# # Make a forward pass of our training data through this layer
# dense1.forward(X)

# # Make a forward pass through activation function
# # it takes the output of first dense layer here
# activation1.forward(dense1.output)

# # # Make a forward pass through second Dense layer
# # # it takes outputs of activation function of first layer as inputs
# # dense2.forward(activation1.output)

# # # Make a forward pass through activation function
# # # it takes the output of second dense layer here
# # activation2.forward(dense2.output)

# # Let's see output of the first few samples:
# print(activation1.output[:5])

# # Perform a forward pass through loss function
# # it takes the output of second dense layer here and returns loss
# loss = loss_function.calculate(activation1.output, y)
# # Print loss value
# print('loss:', loss)



############################################################################################################################################################


# import numpy as np

# class RBFNeuralNetwork:
#     def __init__(self, input_dim, hidden_dim, output_dim, sigma):
#         self.input_dim = input_dim
#         self.hidden_dim = hidden_dim
#         self.output_dim = output_dim
#         self.sigma = sigma
        
#         # Initialize the centers (randomly chosen initially)
#         self.centers = np.random.randn(hidden_dim, input_dim)
#         print(self.centers)
        
#         # Initialize the weights between hidden and output layer
#         self.weights = np.random.randn(hidden_dim, output_dim)
        
#     def _rbf_function(self, x, center):
#         # Compute the Gaussian RBF for a single data point
#         return np.exp(-np.linalg.norm(x - center)**2 / (2 * self.sigma**2))
    
#     def _calculate_activations(self, X):
#         # Calculate activations for each point in X
#         activations = np.zeros((X.shape[0], self.hidden_dim))
#         for i, x in enumerate(X):
#             for j, center in enumerate(self.centers):
#                 activations[i, j] = self._rbf_function(x, center)
#         return activations
    
#     def fit(self, X, y):
#         # Train the network
#         activations = self._calculate_activations(X)
        
#         # Compute the pseudo-inverse of the activations
#         pseudo_inverse = np.linalg.pinv(activations)
        
#         # Solve for the output weights
#         self.weights = np.dot(pseudo_inverse, y)
    
#     def predict(self, X):
#         # Predict using the trained network
#         activations = self._calculate_activations(X)
#         return np.dot(activations, self.weights)

# # Example usage
# if __name__ == "__main__":
#     # Generate some sample data
#     X = np.linspace(-1, 1, 100).reshape(-1, 1)
#     y = np.sin(3 * X) + np.random.normal(0, 0.1, X.shape)
    
#     # Define the RBF Network
#     rbf_net = RBFNeuralNetwork(input_dim=1, hidden_dim=10, output_dim=1, sigma=0.5)
    
#     # Train the network
#     rbf_net.fit(X, y)
    
#     # Make predictions
#     y_pred = rbf_net.predict(X)
    
#     # Plot the results
#     import matplotlib.pyplot as plt
    
#     plt.scatter(X, y, label='True Data')
#     plt.plot(X, y_pred, label='RBF Predictions', color='red')
#     plt.legend()
#     plt.show()





#############################################################################################################################################################



# import numpy as np
# from sklearn.cluster import KMeans
# import matplotlib.pyplot as plt

# class RBFNeuralNetwork:
#     def __init__(self, num_centers, sigma=None):
#         """
#         Initializes the RBF Neural Network.
        
#         Parameters:
#             num_centers (int): Number of RBF centers (hidden neurons).
#             sigma (float, optional): Spread parameter for Gaussian functions. If None, it's computed based on centers.
#         """
#         self.num_centers = num_centers
#         self.sigma = sigma
#         self.centers = None
#         self.weights = None

#     def _rbf_function(self, X, centers, sigma):
#         """
#         Computes the RBF (Gaussian) activation.
        
#         Parameters:
#             X (ndarray): Input data of shape (n_samples, n_features).
#             centers (ndarray): Centers of RBFs of shape (num_centers, n_features).
#             sigma (float): Spread parameter for Gaussian functions.
            
#         Returns:
#             ndarray: RBF activations of shape (n_samples, num_centers).
#         """
#         # Expand dimensions for broadcasting
#         X = X[:, np.newaxis, :]  # Shape: (n_samples, 1, n_features)
#         centers = centers[np.newaxis, :, :]  # Shape: (1, num_centers, n_features)
#         # Compute Euclidean distance between X and centers
#         distances = np.linalg.norm(X - centers, axis=2)  # Shape: (n_samples, num_centers)
#         # Compute Gaussian RBF
#         return np.exp(-(distances ** 2) / (2 * sigma ** 2))
    
#     def _compute_sigma(self):
#         """
#         Computes the sigma value based on the average distance between centers.
#         """
#         if self.centers.shape[0] == 1:
#             # Avoid division by zero if only one center
#             return 1.0
#         # Compute pairwise distances between centers
#         distances = np.linalg.norm(self.centers - self.centers[:, np.newaxis], axis=2)
#         # Compute mean distance between centers
#         mean_distance = np.mean(distances[np.triu_indices_from(distances, k=1)])
#         return mean_distance / np.sqrt(2 * self.num_centers)

#     def fit(self, X, y):
#         """
#         Trains the RBF Network using Least Squares with Cholesky decomposition.
        
#         Parameters:
#             X (ndarray): Training input data of shape (n_samples, n_features).
#             y (ndarray): Training target data of shape (n_samples,) or (n_samples, n_outputs).
#         """
#         n_samples, n_features = X.shape
#         y = y.reshape(-1, 1)  # Ensure y is of shape (n_samples, 1)
        
#         # Step 1: Select centers using K-Means clustering
#         kmeans = KMeans(n_clusters=self.num_centers, random_state=42)
#         kmeans.fit(X)
#         self.centers = kmeans.cluster_centers_
        
#         # Step 2: Compute sigma if not provided
#         if self.sigma is None:
#             self.sigma = self._compute_sigma()
        
#         # Step 3: Compute Design Matrix (Phi)
#         Phi = self._rbf_function(X, self.centers, self.sigma)  # Shape: (n_samples, num_centers)
        
#         # Step 4: Solve for weights using Least Squares with Cholesky decomposition
#         # Compute A = Phi.T @ Phi
#         A = Phi.T @ Phi  # Shape: (num_centers, num_centers)
#         # Add small value to diagonal for numerical stability (regularization)
#         lambda_identity = 1e-8 * np.eye(self.num_centers)
#         A += lambda_identity
#         # Compute b = Phi.T @ y
#         b = Phi.T @ y  # Shape: (num_centers, 1)
#         # Cholesky decomposition
#         L = np.linalg.cholesky(A)  # Lower triangular matrix
#         # Solve Ly = b
#         y_ = np.linalg.solve(L, b)
#         # Solve L.T w = y_
#         self.weights = np.linalg.solve(L.T, y_)  # Shape: (num_centers, 1)

#     def incremental_fit(self, X_new, y_new):
#         """
#         Performs incremental learning using Cholesky Rank-1 updates.
        
#         Parameters:
#             X_new (ndarray): New input data of shape (n_new_samples, n_features).
#             y_new (ndarray): New target data of shape (n_new_samples,) or (n_new_samples, n_outputs).
#         """
#         y_new = y_new.reshape(-1, 1)  # Ensure y_new is of shape (n_new_samples, 1)
        
#         # Compute new Phi for the new data
#         Phi_new = self._rbf_function(X_new, self.centers, self.sigma)  # Shape: (n_new_samples, num_centers)
        
#         # Update A and b
#         # A_new = A_old + Phi_new.T @ Phi_new
#         # b_new = b_old + Phi_new.T @ y_new
#         Phi_new_T_Phi_new = Phi_new.T @ Phi_new
#         Phi_new_T_y_new = Phi_new.T @ y_new
        
#         # Previous A and b
#         A_old = self.Phi_T_Phi if hasattr(self, 'Phi_T_Phi') else np.zeros((self.num_centers, self.num_centers))
#         b_old = self.Phi_T_y if hasattr(self, 'Phi_T_y') else np.zeros((self.num_centers, 1))
        
#         # Updated A and b
#         A_new = A_old + Phi_new_T_Phi_new
#         b_new = b_old + Phi_new_T_y_new
        
#         # Store for future incremental updates
#         self.Phi_T_Phi = A_new
#         self.Phi_T_y = b_new
        
#         # Regularization for numerical stability
#         lambda_identity = 1e-8 * np.eye(self.num_centers)
#         A_new += lambda_identity
        
#         # Cholesky decomposition
#         L = np.linalg.cholesky(A_new)
#         # Solve Ly = b
#         y_ = np.linalg.solve(L, b_new)
#         # Solve L.T w = y_
#         self.weights = np.linalg.solve(L.T, y_)

#     def predict(self, X):
#         """
#         Predicts outputs for given inputs X.
        
#         Parameters:
#             X (ndarray): Input data of shape (n_samples, n_features).
            
#         Returns:
#             ndarray: Predicted outputs of shape (n_samples,).
#         """
#         Phi = self._rbf_function(X, self.centers, self.sigma)  # Shape: (n_samples, num_centers)
#         y_pred = Phi @ self.weights  # Shape: (n_samples, 1)
#         return y_pred.flatten()

# # Example usage
# if __name__ == "__main__":
#     # Generate sample data
#     np.random.seed(42)
#     X_data = np.linspace(-5, 5, 100).reshape(-1, 1)
#     y_data = np.sinc(X_data).ravel() + np.random.normal(0, 0.1, X_data.shape[0])

#     X_train = X_data[0:70]
#     y_train = y_data[0:70]

#     X_test = X_data[70:100]
#     y_test = y_data[70:100]

#     # Initialize and train RBF Network
#     rbf_net = RBFNeuralNetwork(num_centers=10)
#     rbf_net.fit(X_train, y_train)

#     # Predict on training data
#     y_pred_data = rbf_net.predict(X_data)
#     y_pred = rbf_net.predict(X_test)

#     # Plot results
#     plt.figure(figsize=(10, 6))
#     plt.scatter(X_data, y_data, label='Training Data', color='blue', alpha=0.5)
#     plt.plot(X_train, y_train, label='RBF Network Prediction', color='green')
#     plt.plot(X_data, y_pred_data, label='RBF Network Prediction', color='orange')
#     plt.plot(X_test, y_pred, label='RBF Network Prediction', color='red')
#     plt.title('RBF Neural Network Regression')
#     plt.xlabel('X')
#     plt.ylabel('y')
#     plt.legend()
#     plt.show()





###########################################################################################################################################################################################################################################




# import numpy as np
# import matplotlib.pyplot as plt

# def cholesky_rank1_update(L, x):
#     """
#     Perform a rank-1 update of the Cholesky factor L with vector x (add x x^T).
    
#     Parameters:
#     - L: Lower triangular Cholesky factor of the matrix A (A = L L^T).
#     - x: Vector to be added as A_new = A + x x^T.
    
#     Returns:
#     - Updated lower triangular matrix L_new such that L_new L_new^T = A_new.
#     """
#     n = len(x)
#     L_new = L.copy()
#     for k in range(n):
#         r = np.hypot(L_new[k, k], x[k])
#         c = r / L_new[k, k]
#         s = x[k] / L_new[k, k]
#         L_new[k, k] = r
#         if k < n - 1:
#             L_new[k+1:n, k] = (L_new[k+1:n, k] + s * x[k+1:n]) / c
#             x[k+1:n] = c * x[k+1:n] - s * L_new[k+1:n, k]
#     return L_new

# class RBFNeuralNetwork:
#     def __init__(self, input_dim, hidden_dim, sigma, regularization=1e-8):
#         """
#         Initialize the RBF Neural Network.
        
#         Parameters:
#         - input_dim: Dimension of the input data.
#         - hidden_dim: Number of RBF neurons (hidden units).
#         - sigma: Spread parameter for the Gaussian RBF.
#         - regularization: Small value to initialize Phi^T Phi for numerical stability.
#         """
#         self.input_dim = input_dim
#         self.hidden_dim = hidden_dim
#         self.sigma = sigma
#         self.regularization = regularization
        
#         # Initialize RBF centers randomly
#         self.centers = np.random.randn(hidden_dim, input_dim)
        
#         # Initialize Phi^T Phi with regularization
#         self.Phi_T_Phi = self.regularization * np.eye(hidden_dim)
        
#         # Initialize Phi^T y
#         self.Phi_T_y = np.zeros((hidden_dim, 1))
        
#         # Initialize Cholesky factor of Phi^T Phi
#         self.L = np.linalg.cholesky(self.Phi_T_Phi)
        
#     def _rbf_function(self, x, center):
#         """
#         Compute the Gaussian RBF activation.
        
#         Parameters:
#         - x: Input vector.
#         - center: Center of the RBF.
        
#         Returns:
#         - RBF activation value.
#         """
#         return np.exp(-np.linalg.norm(x - center)**2 / (2 * self.sigma**2))
    
#     def _calculate_phi(self, x):
#         """
#         Compute the RBF activations for a single input.
        
#         Parameters:
#         - x: Input vector.
        
#         Returns:
#         - Phi vector (activations) of shape (hidden_dim, 1).
#         """
#         return np.array([self._rbf_function(x, center) for center in self.centers]).reshape(-1, 1)
    
#     def fit(self, X, y):
#         """
#         Train the RBF Neural Network using Least Squares with Cholesky rank-1 updates.
        
#         Parameters:
#         - X: Input data of shape (n_samples, input_dim).
#         - y: Target data of shape (n_samples, 1).
#         """
#         n_samples = X.shape[0]
#         for i in range(n_samples):
#             x_i = X[i, :]
#             y_i = y[i]
            
#             # Compute RBF activations for the current input
#             phi_i = self._calculate_phi(x_i)  # Shape: (hidden_dim, 1)
            
#             # Update Phi^T Phi and Phi^T y
#             self.Phi_T_Phi += phi_i @ phi_i.T  # Outer product, shape: (hidden_dim, hidden_dim)
#             self.Phi_T_y += phi_i * y_i       # Shape: (hidden_dim, 1)
            
#             # Perform Cholesky rank-1 update with phi_i
#             x = phi_i.flatten()
#             self.L = cholesky_rank1_update(self.L, x)
        
#         # After processing all data points, solve for weights
#         # Solve L L^T w = Phi_T_y
#         # First, solve L z = Phi_T_y
#         z = np.linalg.solve(self.L, self.Phi_T_y)
#         # Then, solve L^T w = z
#         w = np.linalg.solve(self.L.T, z)
#         self.weights = w  # Shape: (hidden_dim, 1)
    
#     def predict(self, X):
#         """
#         Predict outputs for given inputs using the trained RBF Network.
        
#         Parameters:
#         - X: Input data of shape (n_samples, input_dim).
        
#         Returns:
#         - Predicted outputs of shape (n_samples, 1).
#         """
#         n_samples = X.shape[0]
#         Phi = np.zeros((n_samples, self.hidden_dim))
#         for i in range(n_samples):
#             Phi[i, :] = np.array([self._rbf_function(X[i, :], center) for center in self.centers])
#         y_pred = Phi @ self.weights  # Shape: (n_samples, 1)
#         return y_pred

# # Example usage
# if __name__ == "__main__":
#     # Generate some sample data: noisy sine wave
#     X_data = np.linspace(-5, 5, 100).reshape(-1, 1)
#     y_data = np.sinc(X_data).ravel() + np.random.normal(0, 0.1, X_data.shape[0])

#     X_train = X_data[0:70]
#     y_train = y_data[0:70]

#     X_test = X_data[70:100]
#     y_test = y_data[70:100]
    
#     # Define the RBF Network parameters
#     input_dim = 10
#     hidden_dim = 10
#     sigma = 3
    
#     # Initialize and train the RBF Network
#     rbf_net = RBFNeuralNetwork(input_dim=input_dim, hidden_dim=hidden_dim, sigma=sigma)
#     rbf_net.fit(X_train, y_train)

#     # Predict on training data
#     y_pred_data = rbf_net.predict(X_data)
#     y_pred = rbf_net.predict(X_test)

#     # Plot results
#     plt.figure(figsize=(10, 6))
#     plt.scatter(X_data, y_data, label='Training Data', color='blue', alpha=0.5)
#     plt.plot(X_train, y_train, label='RBF Network Prediction', color='green')
#     plt.plot(X_data, y_pred_data, label='RBF Network Prediction', color='orange')
#     plt.plot(X_test, y_pred, label='RBF Network Prediction', color='red')
#     plt.title('RBF Neural Network Regression')
#     plt.xlabel('X')
#     plt.ylabel('y')
#     plt.legend()
#     plt.show()













#########################################################################################################################################################################################################################################





# import numpy as np
# import matplotlib.pyplot as plt

# def cholesky_rank1_update(L, x):
#     """
#     Perform a rank-1 update of the Cholesky factor L with vector x (add x x^T).
#     """
#     n = len(x)
#     L_new = L.copy()
#     for k in range(n):
#         r = np.hypot(L_new[k, k], x[k])
#         c = r / L_new[k, k]
#         s = x[k] / L_new[k, k]
#         L_new[k, k] = r
#         if k < n - 1:
#             L_new[k+1:n, k] = (L_new[k+1:n, k] + s * x[k+1:n]) / c
#             x[k+1:n] = c * x[k+1:n] - s * L_new[k+1:n, k]
#     return L_new

# class RBFNeuralNetwork:
#     def __init__(self, input_dim, hidden_dim, sigma, regularization=1e-8):
#         self.input_dim = input_dim
#         self.hidden_dim = hidden_dim
#         self.sigma = sigma
#         self.regularization = regularization
        
#         # Initialize RBF centers randomly
#         self.centers = np.random.randn(hidden_dim, input_dim)
        
#         # Initialize Phi^T Phi with regularization
#         self.Phi_T_Phi = self.regularization * np.eye(hidden_dim)
        
#         # Initialize Phi^T y
#         self.Phi_T_y = np.zeros((hidden_dim, 1))
        
#         # Initialize Cholesky factor of Phi^T Phi
#         self.L = np.linalg.cholesky(self.Phi_T_Phi)
        
#     def _rbf_function(self, x, center):
#         return np.exp(-np.linalg.norm(x - center)**2 / (2 * self.sigma**2))
    
#     def _calculate_phi(self, x):
#         return np.array([self._rbf_function(x, center) for center in self.centers]).reshape(-1, 1)
    
#     def fit(self, X, y):
#         n_samples = X.shape[0]
#         for i in range(n_samples):
#             x_i = X[i, :]
#             y_i = y[i]
            
#             # Compute RBF activations for the current input
#             phi_i = self._calculate_phi(x_i)
            
#             # Update Phi^T Phi and Phi^T y
#             self.Phi_T_Phi += phi_i @ phi_i.T
#             self.Phi_T_y += phi_i * y_i
            
#             # Perform Cholesky rank-1 update with phi_i
#             x = phi_i.flatten()
#             self.L = cholesky_rank1_update(self.L, x)
        
#         # After processing all data points, solve for weights
#         z = np.linalg.solve(self.L, self.Phi_T_y)
#         w = np.linalg.solve(self.L.T, z)
#         self.weights = w
    
#     def predict(self, X):
#         n_samples = X.shape[0]
#         Phi = np.zeros((n_samples, self.hidden_dim))
#         for i in range(n_samples):
#             Phi[i, :] = np.array([self._rbf_function(X[i, :], center) for center in self.centers])
#         y_pred = Phi @ self.weights
#         return y_pred

# def prepare_time_series_data(series, window_size):
#     X, y = [], []
#     for i in range(len(series) - window_size):
#         X.append(series[i:i + window_size])
#         y.append(series[i + window_size])
#     return np.array(X), np.array(y)

# # Example usage
# if __name__ == "__main__":
#     # Generate a synthetic time series: noisy sine wave
#     t = np.linspace(0, 20, 200)
#     series = np.sin(t) + np.random.normal(0, 0.1, t.shape)
    
#     # Prepare the time series data for the RBF network
#     window_size = 5
#     X, y = prepare_time_series_data(series, window_size)
    
#     # Define the RBF Network parameters
#     input_dim = window_size
#     hidden_dim = 10
#     sigma = 1.0
    
#     # Initialize and train the RBF Network
#     rbf_net = RBFNeuralNetwork(input_dim=input_dim, hidden_dim=hidden_dim, sigma=sigma)
#     rbf_net.fit(X, y)
    
#     # Make predictions on the training data
#     y_pred = rbf_net.predict(X)
    
#     # Plot the results
#     plt.figure(figsize=(12, 6))
#     plt.plot(t, series, label='True Time Series', color='blue')
#     plt.plot(t[window_size:], y_pred.flatten(), label='RBF Predictions', color='red', linestyle='--')
#     plt.title('Time Series Prediction using RBF Neural Network')
#     plt.xlabel('Time')
#     plt.ylabel('Value')
#     plt.legend()
#     plt.show()













#########################################################################################################################################################################################################################################







import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def cholesky_rank1_update(L, x):
    """
    Perform a rank-1 update of the Cholesky factor L with vector x (add x x^T).
    """
    n = len(x)
    L_new = L.copy()
    for k in range(n):
        r = np.hypot(L_new[k, k], x[k])
        c = r / L_new[k, k]
        s = x[k] / L_new[k, k]
        L_new[k, k] = r
        if k < n - 1:
            L_new[k+1:n, k] = (L_new[k+1:n, k] + s * x[k+1:n]) / c
            x[k+1:n] = c * x[k+1:n] - s * L_new[k+1:n, k]
    return L_new

class RBFNeuralNetwork:
    def __init__(self, input_dim, hidden_dim, sigma, regularization=10):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.sigma = sigma
        self.regularization = regularization
        
        # Initialize RBF centers randomly
        self.centers = np.random.randn(hidden_dim, input_dim)
        
        # Initialize Phi^T Phi with regularization
        self.Phi_T_Phi = self.regularization * np.eye(hidden_dim)
        
        # Initialize Phi^T y
        self.Phi_T_y = np.zeros((hidden_dim, 1))
        
        # Initialize Cholesky factor of Phi^T Phi
        self.L = np.linalg.cholesky(self.Phi_T_Phi)
        
    def _rbf_function(self, x, center):
        return np.exp(-np.linalg.norm(x - center)**2 / (2 * self.sigma**2))
    
    def _calculate_phi(self, x):
        return np.array([self._rbf_function(x, center) for center in self.centers]).reshape(-1, 1)
    
    def fit(self, X, y):
        n_samples = X.shape[0]
        for i in range(n_samples):
            x_i = X[i, :]
            y_i = y[i]
            
            # Compute RBF activations for the current input
            phi_i = self._calculate_phi(x_i)
            print(phi_i)
            
            # Update Phi^T Phi and Phi^T y
            self.Phi_T_Phi += phi_i @ phi_i.T
            self.Phi_T_y += phi_i * y_i
            
            # Perform Cholesky rank-1 update with phi_i
            x = phi_i.flatten()
            self.L = cholesky_rank1_update(self.L, x)
        
        # After processing all data points, solve for weights
        z = np.linalg.solve(self.L, self.Phi_T_y)
        w = np.linalg.solve(self.L.T, z)
        self.weights = w
    
    def predict(self, X):
        n_samples = X.shape[0]
        Phi = np.zeros((n_samples, self.hidden_dim))
        for i in range(n_samples):
            Phi[i, :] = np.array([self._rbf_function(X[i, :], center) for center in self.centers])
        y_pred = Phi @ self.weights
        return y_pred

def prepare_time_series_data(series, window_size, prediction_horizon):
    X, y = [], []
    for i in range(len(series) - window_size - prediction_horizon + 1):
        X.append(series[i:i + window_size])
        y.append(series[i + window_size + prediction_horizon - 1])
    return np.array(X), np.array(y)

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
        next_input = prediction[-model.input_dim:].reshape(1, -1)
        next_pred = model.predict(next_input)
        prediction = np.append(prediction, next_pred)
    return prediction[-steps_ahead:]

# Example usage
if __name__ == "__main__":
    # # Generate a synthetic time series: noisy sine wave
    # t = np.linspace(0, 1000, 1000)
    # series = np.sin(0.02*t) + np.sin(0.05*t + np.random.normal(0, 0.2, t.shape) ) + np.sin(0.1*t +np.random.normal(0, 0.4, t.shape) ) + np.random.normal(0, 0.1, t.shape)
    # series = series*2 + 5
    
    # print(series)

    # Read Data
    df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[3])

    series = df_wind.values
    series = df_wind.values.astype('float32')

    # print(series)

    t = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[0])
    t = t.values
    # t = t.values.astype('float32')

    # print(t)

    # Prepare the time series data for the RBF network
    window_size = 10
    prediction_horizon = 1
    X, y = prepare_time_series_data(series, window_size, prediction_horizon)
    
    # Define the RBF Network parameters
    input_dim = window_size
    hidden_dim = 10
    sigma = 10
    
    # Initialize and train the RBF Network
    rbf_net = RBFNeuralNetwork(input_dim=input_dim, hidden_dim=hidden_dim, sigma=sigma)
    rbf_net.fit(X, y)
    
    # Predict the 10th step ahead for the entire series
    y_pred = predict_tenth_step_ahead(rbf_net, series, window_size, prediction_horizon)
    
    # Plot the true values and the 10th step ahead predictions
    plt.figure(figsize=(12, 6))
    plt.plot(t, series, label='True Time Series', color='blue')
    plt.plot(t[window_size + prediction_horizon - 1:], y_pred, label='10th Step Ahead Prediction', color='red', linestyle='--')
    plt.title('10th Step Ahead Time Series Prediction using RBF Neural Network')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.show()

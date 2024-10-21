import numpy as np
import pandas as pd
import scipy.linalg as spla

class RBFNeuralNetwork:
    def __init__(self, input_dim, hidden_dim, output_dim, sigma):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.sigma = sigma
        
        # Initialize the centers (randomly chosen initially)
        self.centers = np.random.randn(hidden_dim, input_dim)
        print(self.centers)
        
        # Initialize the weights between hidden and output layer
        self.weights = np.random.randn(hidden_dim, output_dim)
        
    def _rbf_function(self, x, center):
        # Compute the Gaussian RBF for a single data point
        return np.exp(-np.linalg.norm(x - center)**2 / (2 * self.sigma**2))
    
    def _calculate_activations(self, X):
        # Calculate activations for each point in X
        activations = np.zeros((X.shape[0], self.hidden_dim))
        for i, x in enumerate(X):
            for j, center in enumerate(self.centers):
                activations[i, j] = self._rbf_function(x, center)
        return activations
    
    def fit(self, X, y):
        # Train the network
        Phi = self._calculate_activations(X)
        
        # Solve for the weights using QR decomposition
        self.Q, self.R = np.linalg.qr(Phi.T @ Phi)
        self.b = Phi.T @ y
        rhs = self.Q.T @ self.b
        self.weights = spla.solve_triangular(self.R, rhs)

    def update(self, new_X, new_y):
        """
        Update the model when new data (new_X, new_y) arrives using QR rank-1 update.
        """
        # Compute the RBF activation for the new sample new_X
        new_Phi = self._calculate_activations(new_X)
        new_Phi = new_Phi.T
        
        self.Q, self.R = spla.qr_update(self.Q, self.R, new_Phi, new_Phi)
        print(new_y)
        print(new_Phi)

        rhs_updated = self.b + new_y * new_Phi
        print(rhs_updated)
        # Update weights using the updated R matrix
        self.weights = spla.solve_triangular(self.R, self.Q.T @ rhs_updated)
    
    def predict(self, X):
        # Predict using the trained network
        activations = self._calculate_activations(X)
        return np.dot(activations, self.weights)
    
# Time series data preparation function
def prepare_time_series_data(series, window_size, prediction_horizon):
    X, y = [], []
    for i in range(len(series) - window_size - prediction_horizon + 1):
        X.append(series[i:i + window_size])
        y.append(series[i + window_size + prediction_horizon - 1])
    return np.array(X), np.array(y)

# Example usage
if __name__ == "__main__":
    # # Generate some sample data
    # t = np.linspace(-1, 1, 100)
    # series = np.sin(30 * t) + np.random.normal(0, 0.1)
    # print(t)

    # Read Data
    df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[3])

    series = df_wind.values.reshape(-1)
    # print(series)

    t = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[0])
    t = t.values.reshape(-1)

    window_size = 5
    prediction_horizon = 10

    X, y = prepare_time_series_data(series, window_size, prediction_horizon)
    # Split the data: first 50 points for initial fit, rest for updates
    X_initial = X[:50]
    y_initial = y[:50]
    X_remaining = X[50:]
    y_remaining = y[50:]
    
    # Define the RBF Network
    rbf_net = RBFNeuralNetwork(input_dim=window_size, hidden_dim=20, output_dim=1, sigma=5)
    
    # Train the network
    rbf_net.fit(X_initial, y_initial)

    # Incrementally update the RBF network with the remaining data points
    for i in range(X_remaining.shape[0]):
        print(X_remaining.shape[0])
        rbf_net.update(X_remaining[i], y_remaining[i])
    
    # Make predictions
    y_pred = rbf_net.predict(X)
    
    # Plot the results
    import matplotlib.pyplot as plt
    
    plt.scatter(t, series, label='True Data')
    plt.plot(t[window_size + prediction_horizon - 1:], y_pred, label='RBF Predictions', color='red')
    plt.legend()
    plt.show()

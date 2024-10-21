import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

class OnlineKMeans:
    def __init__(self, 
                 n_clusters, 
                 adaptation_rate='auto', 
                 forgetting_factor=None, 
                 random_state=None):
        """
        Initialize the Online K-means model.

        Parameters:
        - n_clusters: int, the number of clusters (K)
        - adaptation_rate: 'auto' or float, the learning rate for updating the centers
                        if 'auto', the learning rate decreases as more points are added to each cluster.
        - forgetting_factor: None or float (0 < forgetting_factor < 1), optional parameter to give more weight to recent points
        - random_state: int, seed for random number generator (optional)
        """
        self.n_clusters = n_clusters
        self.adaptation_rate = adaptation_rate
        self.forgetting_factor = forgetting_factor
        self.centers = None
        self.counts = None
        self.random_state = random_state
    
    def initialize_centers(self, X):
        """
        Initialize the cluster centers using scikit-learn's KMeans (KMeans++ initialization).
        
        Parameters:
        - X: 2D numpy array, data to initialize centers from.
        """
        kmeans = KMeans(n_clusters=self.n_clusters, 
                        random_state=self.random_state)
        kmeans.fit(X)
        self.centers = kmeans.cluster_centers_
        self.counts = np.zeros(self.n_clusters)
        return self.centers

    def _get_adaptation_rate(self, cluster_idx):
        """Compute the learning rate based on the number of points assigned to the cluster."""
        if self.adaptation_rate == 'auto':
            # Decreasing learning rate as more points are added to each cluster
            return 1 / (self.counts[cluster_idx] + 1)
        else:
            # Use a fixed learning rate
            return self.adaptation_rate

    def update(self, x):
        """
        Update the cluster centers with a new data point.

        Parameters:
        - x: new data point (1D numpy array)
        """
        # Step 1: Find the nearest cluster
        distances = np.linalg.norm(self.centers - x, axis=1)
        nearest_cluster_idx = np.argmin(distances)
        # print(f"x{x}")
        # print(f"distances{distances}")
        # print(f"nearest_cluster_idx ===  {nearest_cluster_idx}")

        # Step 2: Update the corresponding cluster center
        if self.forgetting_factor is None:
            # Use standard learning rate
            lr = self._get_adaptation_rate(nearest_cluster_idx)
        else:
            # Use the forgetting factor for non-stationary data
            lr = self.forgetting_factor

        # Move the nearest cluster center slightly towards the new data point
        self.centers[nearest_cluster_idx] = (1 - lr) * self.centers[nearest_cluster_idx] + lr * x
        # print(f"new centres {self.centers[nearest_cluster_idx]}")

        # Step 3: Update the cluster assignment count
        self.counts[nearest_cluster_idx] += 1
        return self.centers

    def predict(self, x):
        """
        Predict the nearest cluster index for a given point.

        Parameters:
        - x: data point (1D numpy array)
        
        Returns:
        - cluster_idx: index of the nearest cluster
        """
        distances = np.linalg.norm(self.centers - x, axis=1)
        return np.argmin(distances)
    
# Time series data preparation function
def prepare_time_series_data(series, window_size, prediction_horizon):
    X, y = [], []
    for i in range(len(series) - window_size - prediction_horizon + 1):
        X.append(series[i:i + window_size])
        y.append(series[i + window_size + prediction_horizon - 1])
    return np.array(X), np.array(y)

# Example usage
if __name__ == "__main__":

    # Read Data
    df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[3])

    series = df_wind.values.reshape(-1)

    t = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[0])
    t = t.values.reshape(-1)

    # Prepare the time series data for RBF network
    window_size = 15
    prediction_horizon = 10
    X, y = prepare_time_series_data(series, window_size, prediction_horizon)

    # Initialize online K-means with 5 clusters
    online_kmeans = OnlineKMeans(n_clusters=5, 
                                 adaptation_rate=0.02, 
                                 forgetting_factor=None, 
                                 random_state=42)

    # Initialize the centers with a random subset of data
    online_kmeans.initialize_centers(X[:100])

    # Stream data points and update centers incrementally
    for x in X:
        online_kmeans.update(x)

    # Print the final cluster centers
    print("Final cluster centers:")
    print(online_kmeans.centers)

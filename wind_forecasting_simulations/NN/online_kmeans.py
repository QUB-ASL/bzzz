import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import calinski_harabasz_score

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
        self.labels = None
        self.inertia = None
    
    def initialize_centers(self, X):
        """
        Initialize the cluster centers using scikit-learn's KMeans (KMeans++ initialization).
        
        Parameters:
        - X: numpy array, data to initialize centers from.
        """
        kmeans = KMeans(n_clusters=self.n_clusters, 
                        random_state=self.random_state)
        kmeans.fit(X)
        self.centers = kmeans.cluster_centers_
        self.counts = np.zeros(self.n_clusters)
        self.labels = kmeans.labels_
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
        self.labels = np.append(self.labels, nearest_cluster_idx)

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
    
    def get_number_of_clusters_elbow_method(self, 
                                            X, 
                                            max_number_of_clusters):
        """
        Plot the elbow curve to find the optimal number of clusters (K) using the inertia value.

        parameters:
        - X: numpy array, data points
        - max_number_of_clusters: int, maximum number of clusters to consider
        """
        inertia = []
        k_values = range(1, max_number_of_clusters)

        for k in k_values:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(X)
            inertia.append(kmeans.inertia_)

        # Plot elbow curve
        plt.plot(k_values, inertia, 'bo-')
        plt.xlabel('Number of clusters (K)')
        plt.ylabel('Inertia')
        plt.title('Elbow Method for Optimal K')
        plt.show()

    def pca_and_plot_clusters(self, X):
        """
        Plot the data points and the cluster centers in 2D using PCA.

        Parameters:
        - X: numpy array, data points
        """
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X)
        centers_pca = pca.transform(self.centers)

        # Explained variance ratio
        print("Explained Variance Ratio:", pca.explained_variance_ratio_)

        # # Get the principal components (loadings)
        # components = pca.components_
        # print("Principal Component Loadings:\n", components)

        plt.figure(figsize=(12, 8))
        plt.scatter(X_pca[:, 0], X_pca[:, 1], c=self.labels, cmap='viridis', marker='o', edgecolor='k')
        plt.scatter(centers_pca[:, 0], centers_pca[:, 1], color='red', label='Cluster Centers')
        plt.xlim(-12, 12) 
        plt.ylim(-12, 12)  
        plt.title('Data Points and Cluster Centers')
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        plt.legend()
        plt.show()

    def plot_centers(self):
        """
        Plot the cluster centers in the original feature space.
        """
        plt.figure(figsize=(12, 8))
        for i, center in enumerate(self.centers):
            plt.plot(center, label=f'Cluster {i+1}')
        plt.title('Cluster Centers')
        plt.xlabel('Feature Index')
        plt.ylabel('Feature Value')
        plt.legend()
        plt.show()

    def calculate_wcss(self, X, labels, centroids):
        """
        Calculate the Within-Cluster Sum of Squares (WCSS) from scratch.

        Parameters:
        - X: np.array, shape (n_samples, n_features)
            The data points used in clustering.
        - labels: np.array, shape (n_samples,)
            Cluster labels for each data point.
        - centroids: np.array, shape (n_clusters, n_features)
            The cluster centroids.

        Returns:
        - wcss: float
            The Within-Cluster Sum of Squares (WCSS).
        """
        wcss = 0
        # Iterate over each cluster
        for k in range(centroids.shape[0]):
            # Get all the data points that belong to cluster k
            cluster_points = X[labels == k]
            
            # Calculate the squared distance between each point and the centroid of cluster k
            distances = np.sum((cluster_points - centroids[k]) ** 2, axis=1)
            
            # Sum all the distances for the cluster
            wcss += np.sum(distances)
        
        return wcss
    
    def calculate_bcss(self, X, labels, centroids):
        """
        Calculate the Between-Cluster Sum of Squares (BCSS).

        Parameters:
        - X: np.array, shape (n_samples, n_features)
            The data points used in clustering.
        - labels: np.array, shape (n_samples,)
            Cluster labels for each data point.
        - centroids: np.array, shape (n_clusters, n_features)
            The cluster centroids.

        Returns:
        - bcss: float
            The Between-Cluster Sum of Squares (BCSS).
        """
        # Compute the global mean of the dataset (overall centroid)
        global_mean = np.mean(X, axis=0)

        # Calculate the number of points in each cluster
        cluster_sizes = np.bincount(labels)

        # Calculate BCSS as the weighted sum of squared distances between cluster centroids and global mean
        bcss = np.sum(cluster_sizes * np.sum((centroids - global_mean) ** 2, axis=1))

        return bcss

    def get_calinski_harabasz_score(self, X):
        """
        Compute the Calinski-Harabasz score for the clustering.

        Parameters:
        - X: numpy array, data points

        Returns:
        - score: float, Calinski-Harabasz score
        """
        return calinski_harabasz_score(X, self.labels)
    
# Time series data preparation function
def prepare_time_series_data(series, window_size, prediction_horizon):
    X, y = [], []
    for i in range(len(series) - window_size - prediction_horizon + 1):
        X.append(series[i:i + window_size])
        y.append(series[i + window_size + prediction_horizon - 1])
    return np.array(X), np.array(y)

# Example usage
if __name__ == "__main__":

    i = 0
    split_data = 1000
    plot_data_every = 250
    last_data = split_data + plot_data_every

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
    
    # online_kmeans.get_number_of_clusters_elbow_method(X, 20)

    # Initialize the centers with a random subset of data
    online_kmeans.initialize_centers(X[:split_data])

    # Plot the initial clusters
    online_kmeans.pca_and_plot_clusters(X[:split_data])

    # Get the initial calinski harabasz score
    print("Calinski-Harabasz Score:", online_kmeans.get_calinski_harabasz_score(X[:split_data]))
    print("wcss:", online_kmeans.calculate_wcss(X[:split_data], online_kmeans.labels, online_kmeans.centers))
    print("bcss:", online_kmeans.calculate_bcss(X[:split_data], online_kmeans.labels, online_kmeans.centers))

    # Plot the initial cluster centers
    # online_kmeans.plot_centers()

    # Stream data points and update centers incrementally
    for x in X[split_data:]:
        online_kmeans.update(x)
        # i = i + 1
        # if i % plot_data_every == 0:
        #     online_kmeans.pca_and_plot_clusters(X[:last_data])
        #     # get the calinski harabasz score
        #     print("Calinski-Harabasz Score:", online_kmeans.get_calinski_harabasz_score(X[:last_data]))
        #     last_data = last_data + plot_data_every
            # plot updated centers
            # online_kmeans.plot_centers()

    # Print the final cluster centers
    # print("Final cluster centers:")
    # print(online_kmeans.centers)
    
    # Plot the final clusters
    online_kmeans.pca_and_plot_clusters(X)

    # Get the final calinski harabasz score
    print("Calinski-Harabasz Score:", online_kmeans.get_calinski_harabasz_score(X))
    print("wcss:", online_kmeans.calculate_wcss(X, online_kmeans.labels, online_kmeans.centers))
    print("bcss:", online_kmeans.calculate_bcss(X, online_kmeans.labels, online_kmeans.centers))

    # Plot the final cluster centers
    # online_kmeans.plot_centers()

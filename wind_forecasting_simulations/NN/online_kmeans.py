import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import calinski_harabasz_score
from matplotlib.animation import FuncAnimation
from collections import defaultdict
from scipy.stats import skew, kurtosis

class OnlineKMeans:
    def __init__(self, 
                 n_clusters, 
                 adaptation_rate='MacQueen',
                 eta_0=None,
                 p=None,
                 momentum=None,
                 random_state=None):
        """
        Initialise the Online K-means model.

        Parameters:
        - n_clusters: int, the number of clusters (K)
        - adaptation_rate: str, the method for adapting the k-means update 
        when new data points are received.
            Options: 'MacQueen', 'Method 5', or a fixed learning rate (float)
        - eta_0: float, initial learning rate (only used if adaptation_rate is 
        'Method 5')
        - p: float, decay constant, 0 < p <= 1 (only used if adaptation_rate 
        is 'Method 5')
        - momentum: float, momentum term for the update
        - random_state: int, seed for random number generator (optional)
        """
        self.n_clusters = n_clusters
        self.adaptation_rate = adaptation_rate
        self.eta_0 = eta_0 
        self.p = p
        self.momentum = momentum
        self.eta_prev = eta_0
        self.centers = None
        self.counts = None
        self.random_state = random_state
        self.labels = None 
        self.cluster_data = defaultdict(list)
    
    def initialise_centres(self, X):
        """
        Initialise the cluster centres using scikit-learn's KMeans 
        (KMeans++ initialisation).

        Parameters:
        - X: numpy array, data to initialise centres from.
        """
        kmeans = KMeans(n_clusters=self.n_clusters, 
                        random_state=self.random_state)
        kmeans.fit(X)
        self.centers = kmeans.cluster_centers_
        self.prev_updates = self.centers
        self.counts = np.zeros(self.n_clusters)
        self.labels = kmeans.labels_

        # Initialise cluster data
        for i, label in enumerate(self.labels):
            self.cluster_data[label].append(X[i])

        return self.centers

    def _get_adaptation_rate(self, cluster_idx):
        """
        Compute the adaptation rate for the cluster.
        """
        if self.adaptation_rate == 'MacQueen':
            # Decreasing learning rate as more points are added to each cluster
            return 1 / (self.counts[cluster_idx] + 1)
        
        elif self.adaptation_rate == 'Method 5':
            t = 0  # Time step 
            # Calculate b as given in the formula
            b = 1 / (self.n_clusters + self.counts[cluster_idx])

            # First term: exponential decay based on time and cluster count
            first_term = np.exp(-self.p * ((t**2) / (self.n_clusters**3)))

            # Second term: decay based on the previous learning rate
            second_term = b * np.exp(-self.n_clusters * self.eta_prev)

            # Calculate eta(t) based on the given 
            eta_t = self.eta_0 * (first_term + second_term)

            # Update eta_prev to the current eta_t for the next iteration
            self.eta_prev = eta_t
            t += 1
            return eta_t
        
        else:
            # Use a fixed learning rate
            return self.adaptation_rate
        
    def check_and_split_cluster(self, cluster_idx):
        """
        Check if a cluster needs splitting based on the 
        Bimodality Coefficient (BC).
        """
        cluster_points = np.array(self.cluster_data[cluster_idx])
        n_points = cluster_points.shape[0]

        if n_points < 50:  # Not enough points to compute BC
            return

        # Calculate skewness and kurtosis
        g = skew(cluster_points, axis=0).mean()
        k = kurtosis(cluster_points, axis=0, fisher=True).mean()

        # Compute the Bimodality Coefficient
        bc = (g**2 + 1) / (k + 3 * ((n_points - 1)**2) / ((n_points - 2) * (n_points - 3)))

        if bc > 0.555:
            self._split_cluster(cluster_idx, cluster_points)

    def _split_cluster(self, cluster_idx, cluster_points):
        local_kmeans = KMeans(n_clusters=2, max_iter=2, random_state=self.random_state)
        local_kmeans.fit(cluster_points)
        local_labels = local_kmeans.labels_
        local_labels[local_labels == 1] = self.n_clusters 
        local_labels[local_labels == 0] = cluster_idx
        local_centers = local_kmeans.cluster_centers_

        # Update the labels of the points in the original cluster
        self.labels[self.labels == cluster_idx] = local_labels

        # Update the first cluster center with one of the splits
        self.centers[cluster_idx] = local_centers[0]
        self.cluster_data[cluster_idx] = cluster_points[local_labels == cluster_idx]
        self.counts[cluster_idx] = len(self.cluster_data[cluster_idx])

        # Add a new cluster for the second split
        self.centers = np.vstack([self.centers, local_centers[1]])
        new_cluster_idx = self.n_clusters
        self.n_clusters += 1

        self.cluster_data[new_cluster_idx] = cluster_points[local_labels == new_cluster_idx]
        self.counts = np.append(self.counts, len(self.cluster_data[new_cluster_idx]))

        # Extend prev_updates to match the new number of clusters
        self.prev_updates = np.vstack([self.prev_updates, local_centers[1]])

    def update(self, x):
        """
        Update the cluster centers when a new data point is received.

        Parameters:
        - x: new data point (1D numpy array)
        """
        # Step 1: Find the nearest cluster
        distances = np.linalg.norm(self.centers - x, axis=1)
        nearest_cluster_idx = np.argmin(distances)
        self.labels = np.append(self.labels, nearest_cluster_idx)

        # Step 2: Update the adaptation rate
        lr = self._get_adaptation_rate(nearest_cluster_idx)

        # Step 3: Update the cluster center
        if self.momentum is not None:
            self.centers[nearest_cluster_idx] = (
                (1 - lr) * self.centers[nearest_cluster_idx] 
                + lr * x 
                + self.momentum * (self.centers[nearest_cluster_idx] - self.prev_updates[nearest_cluster_idx])
            )
            self.prev_updates[nearest_cluster_idx] = self.centers[nearest_cluster_idx]
        else:
            self.centers[nearest_cluster_idx] = (1 - lr) * self.centers[nearest_cluster_idx] + lr * x

        # Step 4: Update cluster data
        self.cluster_data[nearest_cluster_idx] = list(self.cluster_data[nearest_cluster_idx])
        self.cluster_data[nearest_cluster_idx].append(x)
        self.counts[nearest_cluster_idx] += 1

        # Step 5: Check if the cluster needs splitting
        self.check_and_split_cluster(nearest_cluster_idx)

        return self.centers

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
        # print("Explained Variance Ratio:", pca.explained_variance_ratio_)

        # # Get the principal components (loadings)
        # components = pca.components_
        # print("Principal Component Loadings:\n", components)

        plt.figure(figsize=(12, 8))
        plt.scatter(X_pca[:, 0], X_pca[:, 1], c=self.labels, cmap='viridis', marker='o', edgecolor='k')
        plt.scatter(centers_pca[:, 0], centers_pca[:, 1], color='red', label='Cluster Centers')
        plt.xlim(-12, 20) 
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
        wcss = []
        # Iterate over each cluster
        for k in range(centroids.shape[0]):
            # Get all the data points that belong to cluster k
            cluster_points = X[labels == k]
            
            # Calculate the squared distance between each point and the centroid of cluster k
            wcss.append((np.sum((cluster_points - centroids[k]) ** 2))/len(cluster_points))
            
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
        bcss = (np.sum(cluster_sizes * np.sum((centroids - global_mean) ** 2, axis=1))) / len(X)

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

def animation(X, initial_data_end, interval=1000):

    # Initialize online K-means with 5 clusters
    online_kmeans = OnlineKMeans(n_clusters=5, 
                                 adaptation_rate=0.1,
                                #  eta_0=0.02,
                                #  p=0.9,
                                #  momentum=0.9,
                                 random_state=42)

    online_kmeans.initialise_centres(X[:initial_data_end])

    X_pca = np.array([[0,10], [1,10], [2,10], [3,10], [4,10], [5,10], [6,10], [7,10], [8,10], [9,10]])
    colour_labels = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    c = colour_labels

    pca = PCA(n_components=2)
    X_pca = np.vstack([X_pca, pca.fit_transform(X[:initial_data_end])])
    centers_pca = pca.transform(online_kmeans.centers)
    c = np.append(c, online_kmeans.labels)

     # Define the colormap to ensure consistent cluster colors
    cmap = plt.get_cmap('tab10')  # Use a set of 10 distinct colors

    # Set up the main figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 8))

    # Configure the PCA scatter plot (subplot 1)
    ax1.set_xlim(-12, 20)
    ax1.set_ylim(-12, 12)
    ax1.set_title('Data Points and Cluster Centers in PCA Space')
    ax1.set_xlabel('Principal Component 1')
    ax1.set_ylabel('Principal Component 2')
    scatter_points = ax1.scatter(X_pca[:, 0], X_pca[:, 1], c=c, cmap=cmap, edgecolor='k')
    scatter_centers = ax1.scatter(centers_pca[:, 0], centers_pca[:, 1], s = 80 , color='yellow', label='Cluster Centers', edgecolor='darkred')
    ax1.legend()

    def update(frame):
        ax2.clear()
        online_kmeans.update(X[initial_data_end + frame])
        X_pca = pca.transform(X[:initial_data_end + frame])
        centers_pca = pca.transform(online_kmeans.centers)
        scatter_points.set_offsets(X_pca)
        scatter_centers.set_offsets(centers_pca)
        # Update the colors to match new labels
        scatter_points.set_array(online_kmeans.labels[:initial_data_end + frame])

        ax2.set_title('Cluster Centers in Original Feature Space')
        ax2.set_xlabel('Feature Index')
        ax2.set_ylabel('Feature Value')
        ax2.set_ylim(0, 5)
        for i, center in enumerate(online_kmeans.centers):
                ax2.plot(center, label=f'Cluster {i+1}')
        ax2.legend(loc='upper right')

        return scatter_points, scatter_centers
    
    anim = FuncAnimation(fig, update, frames=range(0, len(X)-initial_data_end), interval=interval)

    plt.tight_layout()
    plt.show()

# Example usage
if __name__ == "__main__":

    i = 0
    split_data = 1000
    plot_data_every = 50
    last_data = split_data + plot_data_every

    # Read Data
    df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[8])

    series = df_wind.values.reshape(-1)

    t = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[0])
    t = t.values.reshape(-1)

    # Prepare the time series data for RBF network
    window_size = 15
    prediction_horizon = 10
    X, y = prepare_time_series_data(series, window_size, prediction_horizon)

    animation( X, split_data, -1)

    # # Initialize online K-means with 5 clusters
    # online_kmeans = OnlineKMeans(n_clusters=5, 
    #                              adaptation_rate=0.02,
    #                              eta_0=None,
    #                              p=None, 
    #                              random_state=42)
    
    # # # online_kmeans.get_number_of_clusters_elbow_method(X, 20)

    # # Initialize the centers with a random subset of data
    # online_kmeans.initialize_centers(X[:split_data])

    # # Plot the initial clusters
    # online_kmeans.pca_and_plot_clusters(X[:split_data])

    # # Get the initial calinski harabasz score
    # print("Calinski-Harabasz Score:", online_kmeans.get_calinski_harabasz_score(X[:split_data]))
    # print("wcss:", online_kmeans.calculate_wcss(X[:split_data], online_kmeans.labels, online_kmeans.centers))
    # print("bcss:", online_kmeans.calculate_bcss(X[:split_data], online_kmeans.labels, online_kmeans.centers))

    # # Plot the initial cluster centers
    # online_kmeans.plot_centers()

    # # Stream data points and update centers incrementally
    # for x in X[split_data:]:
    #     online_kmeans.update(x)
    #     i = i + 1
    #     if i % plot_data_every == 0:
    #         online_kmeans.pca_and_plot_clusters(X[:last_data])
    #         # get the calinski harabasz score
    #         print("Calinski-Harabasz Score:", online_kmeans.get_calinski_harabasz_score(X[:last_data]))
    #         last_data = last_data + plot_data_every
    #         # plot updated centers
    #         # online_kmeans.plot_centers()

    # # Print the final cluster centers
    # # print("Final cluster centers:")
    # # print(online_kmeans.centers)
    
    # # Plot the final clusters
    # online_kmeans.pca_and_plot_clusters(X)

    # # Get the final calinski harabasz score
    # print("Calinski-Harabasz Score:", online_kmeans.get_calinski_harabasz_score(X))
    # print("wcss:", online_kmeans.calculate_wcss(X, online_kmeans.labels, online_kmeans.centers))
    # print("bcss:", online_kmeans.calculate_bcss(X, online_kmeans.labels, online_kmeans.centers))

    # # Plot the final cluster centers
    # online_kmeans.plot_centers()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import calinski_harabasz_score
from matplotlib.animation import FuncAnimation
from collections import defaultdict
from scipy.stats import skew, kurtosis
import seaborn as sns
from scipy.stats import gaussian_kde
from scipy.spatial import ConvexHull, Delaunay
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
from matplotlib.animation import PillowWriter

plt.rc('pdf',fonttype = 42)
plt.rc('font',family='Times New Roman')

class OnlineKMeans:
    def __init__(self, 
                 n_clusters, 
                 adaptation_rate='MacQueen',
                 eta_0=None,
                 p=None,
                 momentum=None,
                 random_state=None,
                 initial_centers=None):
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
        self.centers = initial_centers
        self.counts = np.zeros(self.n_clusters)
        self.random_state = random_state
        self.labels = None 
        self.cluster_data = defaultdict(list)
        self.t = 0
        self.last_split_cluster_idx = None
    
    def initialise_centres(self, X=None):
        """
        Initialise the cluster centres using scikit-learn's KMeans 
        (KMeans++ initialisation).

        Parameters:
        - X: numpy array, data to initialise centres from.
        """
        if self.centers is not None:
            if X is None:
                X = self.centers  # Use the provided centers as dummy data for fitting
            init_param = self.centers
        else:
            if X is None:
                raise ValueError("X must be provided if initial centers are not set.")
            init_param = 'k-means++'

        kmeans = KMeans(n_clusters=self.n_clusters,
                        init=init_param, 
                        random_state=self.random_state)
        kmeans.fit(X)
        self.centers = kmeans.cluster_centers_
        self.prev_updates = self.centers
        self.labels = kmeans.labels_

        # Initialise cluster data
        for i, label in enumerate(self.labels):
            self.cluster_data[label].append(X[i])
            self.counts[label] = len(self.cluster_data[label])

        return self.centers

    def _get_adaptation_rate(self, cluster_idx):
        """
        Compute the adaptation rate for the cluster.
        """
        if self.adaptation_rate == 'MacQueen':
            # Decreasing learning rate as more points are added to each cluster
            # return 1 / (self.counts[cluster_idx] + 1)
            return 300 / (self.counts[cluster_idx] + (self.counts[cluster_idx]-320)*300)
        
        elif self.adaptation_rate == 'Method 5':
            # Calculate b as given in the formula
            b = 1 / (self.n_clusters + self.counts[cluster_idx])

            # First term: exponential decay based on time and cluster count
            first_term = np.exp(-self.p * ((self.t**2) / (self.n_clusters**3)))

            # Second term: decay based on the previous learning rate
            second_term = b * np.exp(-self.n_clusters * self.eta_prev)

            # Calculate eta(t) based on the given 
            eta_t = self.eta_0 * (first_term + second_term)

            # Update eta_prev to the current eta_t for the next iteration
            self.eta_prev = eta_t
            self.t += 1
            return eta_t
        
        else:
            # Use a fixed learning rate
            return self.adaptation_rate
        
    def mardia_skewness_kurtosis(self, X):
        """
        Computes Mardia's multivariate skewness and kurtosis.

        Parameters
        ----------
        X : array_like, shape (n_samples, n_features)
            The data matrix.

        Returns
        -------
        skewness : float
            Mardia’s multivariate skewness b_{1,d}.
        kurtosis : float
            Mardia’s multivariate kurtosis b_{2,d}.
        """
        X = np.asarray(X)
        n, d = X.shape

        # 1. centre and covariance (population)
        mean = X.mean(axis=0)
        S = np.cov(X, rowvar=False, ddof=0)

        # 2. inverse (pseudo-inverse for stability)
        S_inv = np.linalg.pinv(S)

        # 3. demean
        diffs = X - mean

        # 4. pairwise Mahalanobis inner products
        D = diffs @ S_inv @ diffs.T   # shape (n, n), D[i,j] = (x_i-μ)^T S⁻¹ (x_j-μ)

        # 5. skewness and kurtosis
        b1d = D.ravel().dot(D.ravel()**2) / (n**2)        # ∑ D_ij^3 / n^2
        b2d = np.sum(np.diag(D)**2) / n                   # ∑ (D_ii)^2 / n

        return b1d, b2d
    
    
    # def check_and_split_cluster(self, cluster_idx):
    #     """
    #     Check if a cluster is potentially multimodal using the Bimodality Coefficient (BC).
    #     Evaluates BC along all feature axes and the diagonal direction e.
    #     Splits the cluster if any BC exceeds the threshold (typically 0.6).
    #     """
    #     cluster_points = np.array(self.cluster_data[cluster_idx])
    #     n_points, n_dims = cluster_points.shape

    #     if n_points < 50:
    #         return  # Not enough data for stable estimation

    #     # Threshold for BC above which we consider the distribution bimodal
    #     bc_threshold = 0.6

    #     # Function to compute BC given a 1D projection
    #     def compute_bc(x):
    #         g = skew(x)
    #         k = kurtosis(x, fisher=True)
    #         if np.isnan(g) or np.isnan(k) or k <= 0:
    #             return 0.0  # Safe default
    #         denom = k + 3 * ((n_points - 1)**2) / ((n_points - 2) * (n_points - 3))
    #         return (g**2 + 1) / denom

    #     # Check BC in each feature direction
    #     for dim in range(n_dims):
    #         x = cluster_points[:, dim]
    #         bc = compute_bc(x)
    #         if bc > bc_threshold:
    #             print(f"Cluster {cluster_idx} is bimodal along feature axis {dim}. BC = {bc:.3f}. SPLITTING...")
    #             self._split_cluster(cluster_idx, cluster_points)
    #             return

    #     # Check BC in the diagonal direction
    #     e = np.ones(n_dims) / np.sqrt(n_dims)
    #     x_proj = cluster_points @ e  # Project onto diagonal
    #     bc_diag = compute_bc(x_proj)
    #     if bc_diag > bc_threshold:
    #         print(f"Cluster {cluster_idx} is bimodal along diagonal direction. BC = {bc_diag:.3f}. SPLITTING...")
    #         self._split_cluster(cluster_idx, cluster_points)
    #         return
    
        
    # def check_and_split_cluster(self, cluster_idx):
    #     """
    #     Check if a cluster needs splitting based on univariate
    #     Bimodality Coefficient (BC) computed per dimension.
    #     """
    #     cluster_points = np.array(self.cluster_data[cluster_idx])
    #     n_points, n_dims = cluster_points.shape

    #     if n_points < 50:
    #         return  # Not enough data for stable BC

    #     # Compute BC per dimension
    #     for dim in range(n_dims):
    #         x = cluster_points[:, dim]
    #         g = skew(x)
    #         k = kurtosis(x, fisher=True)

    #         # Avoid division by zero or invalid kurtosis
    #         if np.isnan(g) or np.isnan(k) or k <= 0:
    #             continue

    #         # Pfister et al. BC formula (adjusted for small samples)
    #         denom = k + 3 * ((n_points - 1)**2) / ((n_points - 2) * (n_points - 3))
    #         bc = (g**2 + 1) / denom

    #         if bc > 0.6:  # Threshold may be tuned
    #             print(f"Cluster {cluster_idx} is bimodal along dimension {dim}. BC = {bc:.3f}. SPLITTING...")
    #             self._split_cluster(cluster_idx, cluster_points)
    #             return  # Stop after first trigger
            
            
    def check_and_split_cluster(self, cluster_idx):
        """
        Check if a cluster needs splitting based on the 
        Bimodality Coefficient (BC).
        """
        cluster_points = np.array(self.cluster_data[cluster_idx])
        n_points = cluster_points.shape[0]

        # print(self.centers)

        # print(self.centers[cluster_idx].reshape(1, -1))

        if n_points < 50:  # Not enough points to compute BC
            return

        # Calculate skewness and kurtosis
        g = skew(cluster_points, axis=0).mean()
        k = kurtosis(cluster_points, axis=0, fisher=True).mean()

        # Compute the Bimodality Coefficient
        bc = (g**2 + 1) / (k + 3 * ((n_points - 1)**2) / ((n_points - 2) * (n_points - 3)))

        if bc > 0.6:
            print(f"Cluster {cluster_idx} is bimodal. SPLITTING...")
            self._split_cluster(cluster_idx, cluster_points)

    def _split_cluster(self, cluster_idx, cluster_points):
        # print(f"Splitting cluster {cluster_idx}...")
        total_count = np.sum(self.counts)
        # print(f"At count: {total_count}")
        # local_kmeans = KMeans(n_clusters=2, max_iter=2, random_state=self.random_state)
        local_kmeans = KMeans(n_clusters=2, init=np.vstack([self.centers[cluster_idx].reshape(1, -1),self.centers[cluster_idx].reshape(1, -1)]), n_init=1,
                              max_iter=2, random_state=self.random_state)
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

        self.last_split_cluster_idx = cluster_idx

    def get_last_split_cluster_idx(self):
        """
        Get the index of the last split cluster.
        """
        return self.last_split_cluster_idx

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
        plt.scatter(centers_pca[:, 0], centers_pca[:, 1], color='red', label='Cluster Centres')
        plt.xlim(-12, 20) 
        plt.ylim(-12, 12)  
        plt.title('Data Points and Cluster Centres')
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        plt.legend()
        plt.show()

    def plot_centers(self):
        """
        Plot the cluster centres in the original feature space.
        """
        plt.figure(figsize=(12, 8))
        for i, center in enumerate(self.centers):
            plt.plot(center, label=f'Cluster {i+1}')
        plt.title('Cluster Centres')
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

# def animation(X, initial_data_end, interval=1000):

#     # centres = np.array([[-0.20972233, -0.2075368,  -0.20699677, -0.20798667, -0.21016227],
#     #                 [1.89863988, 1.89980074, 1.90048287, 1.90000685, 1.89857222],
#     #                 [-1.44886963, -1.45559866, -1.45785451, -1.45542487, -1.44849511],
#     #                 [4.12300518, 4.14316454, 4.14997769, 4.14235578, 4.12118884],
#     #                 [-0.58886111, -0.58867664, -0.58850176, -0.58816616, -0.58827087],
#     #                 [0.61804511, 0.6147604,  0.61399737, 0.61528543, 0.61846244],
#     #                 [3.3329001,  3.34601816, 3.35037454, 3.34577901, 3.33216633],
#     #                 [1.49516368, 1.49328723, 1.49279968, 1.49365202, 1.49568017],
#     #                 [-1.02574085, -1.02898248, -1.03007778, -1.02914034, -1.02621726],
#     #                 [0.1966223,  0.19444408,  0.19356163,  0.19399402,  0.19615315],
#     #                 [2.30409389, 2.30806527, 2.30891348, 2.30738084, 2.30362371],
#     #                 [-1.95683855, -1.96699022, -1.97060372, -1.96761252, -1.95811761],
#     #                 [1.07230902, 1.06854207, 1.06710083, 1.06845743, 1.07230768],
#     #                 [-2.75216366, -2.76677145, -2.771969, -2.76638428, -2.75015501],
#     #                 [2.76905847, 2.77678981, 2.77961552, 2.77726856, 2.76999329]])

#     # Initialize online K-means with 5 clusters
#     online_kmeans = OnlineKMeans(n_clusters=5, 
#                                  adaptation_rate=0.03,
#                                 #  eta_0=0.9,
#                                 #  p=0.1,
#                                 #  momentum=0.9,
#                                  random_state=42)

#     online_kmeans.initialise_centres(X[:initial_data_end])

#     X_pca = np.array([[0,10], [1,10], [2,10], [3,10], [4,10], [5,10], [6,10], [7,10], [8,10], [9,10]])
#     colour_labels = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
#     c = colour_labels

#     pca = PCA(n_components=2)
#     X_pca = np.vstack([X_pca, pca.fit_transform(X[:initial_data_end])])
#     centers_pca = pca.transform(online_kmeans.centers)
#     c = np.append(c, online_kmeans.labels)

#      # Define the colormap to ensure consistent cluster colors
#     cmap = plt.get_cmap('tab10')  # Use a set of 10 distinct colors

#     # Set up the main figure with two subplots
#     # fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 8))
#     fig = plt.figure(figsize=(16, 8))
#     gs = gridspec.GridSpec(5, 1, height_ratios=[3, 3, 3, 2, 2]) 
#     ax1 = fig.add_subplot(gs[:3])  # Takes the first two rows
#     ax2 = fig.add_subplot(gs[3:])  # Takes the last row

#     # Configure the PCA scatter plot (subplot 1)
#     ax1.set_xlim(-11, 17)
#     ax1.set_ylim(-6, 6)
#     ax1.set_title('Data Points and Cluster Centers in PCA Space', fontsize=32)
#     ax1.set_xlabel('Principal Component 1', fontsize=23)
#     ax1.set_ylabel('Principal Component 2', fontsize=23)
#     scatter_points = ax1.scatter(X_pca[:, 0], X_pca[:, 1], s=120, c=c, cmap=cmap, edgecolor='k')
#     scatter_centers = ax1.scatter(centers_pca[:, 0], centers_pca[:, 1], s = 500, color='yellow', label='Cluster Centers', edgecolor='darkred')
#     ax1.legend(fontsize=20)

#     def update(frame):
#         ax2.clear()
#         online_kmeans.update(X[initial_data_end + frame])
#         X_pca = pca.transform(X[:initial_data_end + frame])
#         centers_pca = pca.transform(online_kmeans.centers)
#         scatter_points.set_offsets(X_pca)
#         scatter_centers.set_offsets(centers_pca)
#         # Update the colors to match new labels
#         scatter_points.set_array(online_kmeans.labels[:initial_data_end + frame])

#         ax2.set_title('Cluster Centers in Original Feature Space', fontsize=32)
#         ax2.set_xlabel('Feature Index', fontsize=23)
#         ax2.set_ylabel('Feature Value', fontsize=23)
#         ax2.set_ylim(0, 5)
#         for i, center in enumerate(online_kmeans.centers):
#                 ax2.plot(center, label=f'Cluster {i+1}', linewidth=4)
#         ax2.legend(loc='upper right', fontsize=20)

#         return scatter_points, scatter_centers
    
#     anim = FuncAnimation(fig, update, frames=range(0, len(X)-initial_data_end), interval=interval)

#     plt.tight_layout()
#     plt.show()

def animation(X, initial_data_end, interval=1000):
    # Initialize online K-means with 5 clusters
    online_kmeans = OnlineKMeans(n_clusters=2, 
                                 adaptation_rate="MacQueen",
                                 random_state=42)
    online_kmeans.initialise_centres(X[:initial_data_end])

    number_of_clusters = online_kmeans.n_clusters

    pca = PCA(n_components=2)
    X_pca_all = pca.fit_transform(X)
    centers_pca = pca.transform(online_kmeans.centers)

    # Set up figure
    fig = plt.figure(figsize=(8, 5))
    gs = gridspec.GridSpec(5, 1, height_ratios=[3, 3, 3, 2, 2]) 
    ax1 = fig.add_subplot(gs[:3])  # PCA space
    ax2 = fig.add_subplot(gs[3:])  # Feature space

    ax1.set_xlim(-11, 18)
    ax1.set_ylim(-5, 4.5)
    ax1.set_title('Cluster Density and Centres in PCA Space', fontsize=16)
    ax1.set_xlabel('Principal Component 1', fontsize=14)
    ax1.set_ylabel('Principal Component 2', fontsize=14)
    ax1.tick_params(axis='both', labelsize=14)

    cluster_colors = ['Blues', 'Oranges', 'Greens', 'Reds', 'Purples', 'Greys', 'PuRd']
    plot_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',  'tab:grey', 'tab:pink']
    marker_colors_temp = [plt.cm.tab20(i) for i in range(20)]
    marker_colors = marker_colors_temp[1], marker_colors_temp[3], marker_colors_temp[5], marker_colors_temp[7], marker_colors_temp[9], marker_colors_temp[15], marker_colors_temp[13]
    
    # Store KDE data to avoid recalculating
    cluster_kde_data = {}
    kde_cache = {}

    # === FIRST FRAME: Compute KDE for all clusters ===
    labels_subset = np.array(online_kmeans.labels[:initial_data_end])  # Convert to array for indexing

    for cluster_idx in range(online_kmeans.n_clusters):
        cluster_points = X_pca_all[:initial_data_end][labels_subset == cluster_idx]  
        if len(cluster_points) > 5:
            cluster_kde_data[cluster_idx] = cluster_points
            kde = gaussian_kde(cluster_points.T, bw_method=0.3)  # Reduced bandwidth for smoother edges

            # Use dynamic padding around the data to avoid box shape
            x_min, x_max = cluster_points[:, 0].min(), cluster_points[:, 0].max()
            y_min, y_max = cluster_points[:, 1].min(), cluster_points[:, 1].max()
            x_padding = (x_max - x_min) * 0.1  # 10% padding
            y_padding = (y_max - y_min) * 0.1  # 10% padding
            x_grid, y_grid = np.meshgrid(np.linspace(x_min - x_padding, x_max + x_padding, 100), 
                                         np.linspace(y_min - y_padding, y_max + y_padding, 100))
            density = kde(np.vstack([x_grid.ravel(), y_grid.ravel()])).reshape(x_grid.shape)
            
            kde_cache[cluster_idx] = (x_grid, y_grid, density)

        # Get handles and labels from one axis
        labels = [f'Cluster {i+1}' for i in range(online_kmeans.n_clusters)]
        handles = [Line2D([0], [0], marker='o', linestyle='None', color=marker_colors[i], markeredgewidth=5, markerfacecolor=plot_colors[i], markersize=20, label=labels[i]) for i in range(online_kmeans.n_clusters)]

        # Place shared legend outside
        # fig.legend(handles, labels, loc='center left', fontsize=20, bbox_to_anchor=(0,1.8), bbox_transform=ax2.transAxes, ncol=2)

    def update(frame, number_of_clusters=number_of_clusters):
        ax2.clear()
        ax1.clear()
        ax1.set_xlim(-11, 18)
        ax1.set_ylim(-5, 4.5)
        ax1.set_title('Cluster Density and Centres in PCA Space', fontsize=16)
        ax1.set_xlabel('Principal Component 1', fontsize=14)
        ax1.set_ylabel('Principal Component 2', fontsize=14)
        ax1.tick_params(axis='both', labelsize=14)

        # Update clustering with a new point
        new_point = X[initial_data_end + frame]
        online_kmeans.update(new_point)

        centers_pca = pca.transform(online_kmeans.centers)
        X_pca = X_pca_all[:initial_data_end + frame]

        new_cluster = online_kmeans.labels[initial_data_end + frame]
        labels_subset = np.array(online_kmeans.labels[:initial_data_end + frame]) 

        cluster_points = X_pca[labels_subset == new_cluster] 

        if len(cluster_points) > 5:
            cluster_kde_data[new_cluster] = cluster_points
            kde = gaussian_kde(cluster_points.T, bw_method=0.3)  # Reduced bandwidth for smoother edges

            # Adjust dynamic padding to smooth borders
            x_min, x_max = cluster_points[:, 0].min(), cluster_points[:, 0].max()
            y_min, y_max = cluster_points[:, 1].min(), cluster_points[:, 1].max()
            x_padding = (x_max - x_min) * 0.2  # 10% padding
            y_padding = (y_max - y_min) * 0.2  # 10% padding
            x_grid, y_grid = np.meshgrid(np.linspace(x_min - x_padding, x_max + x_padding, 100), 
                                         np.linspace(y_min - y_padding, y_max + y_padding, 100))
            density = kde(np.vstack([x_grid.ravel(), y_grid.ravel()])).reshape(x_grid.shape)

            kde_cache[new_cluster] = (x_grid, y_grid, density)

        # Plot all stored KDEs with smooth contours
        for cluster_idx, (x_grid, y_grid, density) in kde_cache.items():
            # Plot filled contours for all inner levels, but avoid filling the outermost one
            contour_levels = np.linspace(np.min(density), np.max(density), 10)
            
            # Plot the inner contours with filling
            ax1.contourf(x_grid, y_grid, density, levels=contour_levels[1:], cmap=cluster_colors[cluster_idx], alpha=0.5)
            ax1.contourf(x_grid, y_grid, density, levels=contour_levels[3:], cmap=cluster_colors[cluster_idx], alpha=1)
            
        if np.sum(online_kmeans.counts) > 500:
            #Plot points in PCA space
            plot_x_y = np.array([[0,10], [1,10], [2,10], [3,10], [4,10], [5,10], [6,10], [7,10], [8,10], [9,10]])
            plot_x_y = np.vstack([plot_x_y, X_pca[500:]])
            colour_labels = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
            colour_labels = np.append(colour_labels, online_kmeans.labels[500:initial_data_end + frame])
            ax1.scatter(plot_x_y[:, 0], plot_x_y[:, 1], s=40, alpha=1, c=colour_labels, cmap='tab10', edgecolor='k')
            # print(online_kmeans.labels[1210:initial_data_end + frame])

        # Plot cluster centers
        ax1.scatter(centers_pca[:, 0], centers_pca[:, 1], s=200, color='yellow', label='Cluster Centres', edgecolor='darkred')
        ax1.legend(loc='upper left', fontsize=10)

        # Define x-ticks: 10 time steps from t-9 to t
        time_labels = [f't-{14 - i}' if i < 14 else 't' for i in range(15)]
        x_positions = list(range(15))  # x-axis positions: 0 through 9
        ax2.set_xticks(x_positions)
        ax2.set_xticklabels(time_labels)

        # Feature space visualization
        ax2.set_ylim(0, 6.2)
        ax2.set_yticks(np.arange(0, 7, 2))
        ax2.set_xlim(-2, 14.2)
        ax2.set_title('Cluster Centres in Feature Space', fontsize=16)
        ax2.set_xlabel('Temporal Index of RBF Centre', fontsize=14)
        ax2.set_ylabel('Wind Velocity - m/s', fontsize=14)
        ax2.tick_params(axis='both', labelsize=14)
        for i, center in enumerate(online_kmeans.centers):
            reversed_center = center[::-1]
            ax2.plot(reversed_center, label=f'Centre {i+1}', linewidth=3, color=plot_colors[i % len(plot_colors)])
        ax2.legend(loc='upper left', fontsize=10)
        

        if online_kmeans.n_clusters > number_of_clusters:
            # Get handles and labels from one axis
            labels = [f'Cluster {i+1}' for i in range(online_kmeans.n_clusters)]
            handles = [Line2D([0], [0], marker='o', linestyle='None', color=marker_colors[i], markeredgewidth=5, markerfacecolor=plot_colors[i], markersize=20, label=labels[i]) for i in range(online_kmeans.n_clusters)]

            # Place shared legend outside
            # fig.legend(handles, labels, loc='center left', fontsize=20, bbox_to_anchor=(0,1.8), bbox_transform=ax2.transAxes, ncol=2 )
            # number_of_clusters = online_kmeans.n_clusters

        if np.sum(online_kmeans.counts) > 500:
            fig.savefig(f'changing_eta_frames_3/frame_{int(np.sum(online_kmeans.counts)-500)}.png', dpi=300, bbox_inches='tight')

        # if np.sum(online_kmeans.counts) == 1958:
        #     fig.savefig('raspberry/data/Split_cluster.pdf', dpi=600, bbox_inches='tight')

        # fig.savefig('raspberry/data/TEST.svg', dpi=600, bbox_inches='tight')

    anim = FuncAnimation(fig, update, frames=range(0, len(X)-initial_data_end), interval=interval)

    plt.tight_layout(rect=[0, 0.02, 1, 1])
    plt.show()

    # anim.save('raspberry/data/TEST.gif', writer=PillowWriter(fps=5))


# Example usage
if __name__ == "__main__":

    i = 0
    split_data = 500
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
    # online_kmeans.initialise_centres(X[:split_data])

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

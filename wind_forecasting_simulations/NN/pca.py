import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

import matplotlib.pyplot as plt

# Parameters for training and testing
window_size = 15
prediction_horizon = 10

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

# Read Data
df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[3])

series = df_wind.values.reshape(-1)

t = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[0])
t = t.values.reshape(-1)

# Prepare the time series data for RBF network
data, y = prepare_time_series_data(series, window_size, prediction_horizon)

# Standardize the data
data_standardized = (data - data.mean()) / data.std()
print(data_standardized)

# Perform PCA
pca = PCA(n_components=2)  # You can change the number of components
principal_components = pca.fit_transform(data_standardized)

# Create a DataFrame with the principal components
principal_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])

# Plot the explained variance
plt.figure(figsize=(8, 6))
plt.plot(np.cumsum(pca.explained_variance_ratio_))
plt.xlabel('Number of Components')
plt.ylabel('Variance Explained')
plt.title('Explained Variance by Number of Components')
plt.show()

# Save the principal components to a CSV file
# principal_df.to_csv('principal_components.csv', index=False)

# print("PCA completed and results saved to 'principal_components.csv'")
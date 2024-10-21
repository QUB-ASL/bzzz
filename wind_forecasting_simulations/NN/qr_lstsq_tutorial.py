import numpy as np
import scipy as sp
import scipy.linalg as spla
from sklearn.cluster import KMeans


def _rbf_function(x, center):
        # Gaussian RBF
        return np.exp(-np.linalg.norm(x - center)**2 / (2 * sigma**2))
    
def _calculate_phi(X):
        # Calculate the design matrix Phi using the RBF function
        n_samples = X.shape[0]
        Phi = np.zeros((n_samples, num_centers))
        for i in range(n_samples):
            for j in range(num_centers):
                Phi[i, j] = _rbf_function(X[i], centers[j])
        return Phi

n_samples = 6
n_features = 2
num_centers = 3

x = np.random.randn(n_samples, n_features)
y = np.random.randn(n_samples, 1)
# print(f"x: {x}")
# print(f"y: {y}")

I = np.eye(num_centers)
regulariser = 0.5

# Use KMeans to select the centers for the RBFs
kmeans = KMeans(n_clusters=num_centers, random_state=42).fit(x)
centers = kmeans.cluster_centers_

# calculate it based on the distances between centers
dists = np.linalg.norm(centers[:, np.newaxis] - centers, axis=2)
sigma = np.mean(dists)

A = _calculate_phi(x)
# print(f"A: {A}")

Q, R = np.linalg.qr(A.T @ A)
b = A.T @ y
rhs = Q.T @ b
lhs = R + regulariser * I
x_star = spla.solve_triangular(lhs, rhs)
# print(f"b: {b}")
# print(f"rhs: {rhs}")
print(f"Q: {Q}")
# print(f"R: {R}")
# print(f"x_star: {x_star}")


# # Test
# x_star_true = np.linalg.lstsq(A, y)[0]
# print(x_star_true)
# err = x_star- x_star_true
# print(f"Error: {np.linalg.norm(err, np.inf)}")




x_n = np.random.randn(3000, n_features)
y_new = np.random.randn(3000, 1)
# print(f"x_n: {x_n}")
# print(f"y_new: {y_new}")

import time

start = time.time()
for w in range(1):
    for i in range(x_n.shape[0]):
        # print(x_n.shape[0])
        # print(x_n)
        # print(x_n[i].reshape(1, -1))

        x_new = _calculate_phi(x_n[i].reshape(1, -1))
        x_new = x_new.T
        # print(f"A_new: {x_new}")

        Q, R = spla.qr_update(Q, R, x_new, x_new)
        b = b + y_new[i] * x_new
        rhs = Q.T @ b
        lhs = R + regulariser * I
        x_star = spla.solve_triangular(lhs, rhs)
        # print(f"b: {b}")
        # print(f"rhs: {rhs}")
        # print(f"Q: {Q}")
        # print(f"R: {R}")
        # print(f"x_star: {x_star}")
        # print(f"x_star_updated: {x_star_updated}")
end = time.time()
print((end - start)/10000)

# # Test
# A_big = np.vstack((A, x_new))
# y_big = np.vstack((y, y_new))
# print(A_big)

# errQRupdate = Qnew @ Rnew - A_big.T @ A_big
# errRhsNew = rhs_updated - (A_big.T @ y_big)
# # print(errRhsNew)
# x_star_updated_true = np.linalg.lstsq(A_big, y_big, rcond=1e-6)[0]

# err_updated = x_star_updated_true - x_star_updated
# # print(err_updated)
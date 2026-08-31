# import numpy as np

# class Kriging:
#     def __init__(self, sigma2=1.0, zeta=10.0):
#         self.sigma2 = sigma2
#         self.zeta = zeta

#     def _exponential_covariance(self, d):
#         return self.sigma2 * np.exp(-d / self.zeta)

#     def interpolate(self, known_locs, known_values, query_loc):
#         n_points = known_locs.shape[0]
#         if known_values.shape[0] != n_points:
#             raise ValueError("Mismatch between number of locations and number of values.")

#         D = np.linalg.norm(known_locs[:, None, :] - known_locs[None, :, :], axis=2)
#         C = self._exponential_covariance(D)

#         C_ext = np.ones((n_points + 1, n_points + 1))
#         C_ext[:n_points, :n_points] = C
#         C_ext[n_points, n_points] = 0

#         d_star = np.linalg.norm(known_locs - query_loc, axis=1)
#         c_star = self._exponential_covariance(d_star)

#         rhs = np.append(c_star, 1.0)

#         try:
#             weights = np.linalg.solve(C_ext, rhs)
#         except np.linalg.LinAlgError:
#             raise ValueError("Covariance matrix is singular or ill-conditioned.")

#         varpi = weights[:n_points]
#         interpolated_value = np.dot(varpi, known_values)

#         return interpolated_value


# class GaussianProcess:
#     def __init__(self, sigma2=1.0, zeta=10.0, noise=1e-8):
#         self.sigma2 = sigma2
#         self.zeta = zeta
#         self.noise = noise

#     def _exponential_covariance(self, d):
#         return self.sigma2 * np.exp(-d / self.zeta)

#     def fit(self, X_train, y_train):
#         self.X_train = X_train
#         self.y_train = y_train

#         D = np.linalg.norm(X_train[:, None, :] - X_train[None, :, :], axis=2)
#         self.K = self._exponential_covariance(D) + self.noise * np.eye(len(X_train))

#         try:
#             self.K_inv = np.linalg.inv(self.K)
#         except np.linalg.LinAlgError:
#             raise ValueError("Training covariance matrix is singular or ill-conditioned.")

#     def predict(self, X_query):
#         D_star = np.linalg.norm(self.X_train[:, None, :] - X_query[None, :, :], axis=2)
#         K_star = self._exponential_covariance(D_star)

#         y_pred = K_star.T @ self.K_inv @ self.y_train
#         return y_pred


# class KrigingRBFParameters(Kriging):
#     def interpolate_parameters(self, known_locs, centers_list, weights_list, query_loc):
#         """
#         Interpolate RBF centers and weights at query location using Kriging.
#         Only interpolate over available centers/weights at each position.
#         """
#         n_points = known_locs.shape[0]

#         max_centers = max(center.shape[0] for center in centers_list)
#         center_dim = centers_list[0].shape[1]

#         interpolated_centers = np.zeros((max_centers, center_dim))
#         interpolated_weights = np.zeros(max_centers)

#         for j in range(max_centers):
#             # Find which models have center j available
#             available_idx = [k for k in range(n_points) if centers_list[k].shape[0] > j]

#             if not available_idx:
#                 continue  # No data for this center

#             available_locs = known_locs[available_idx]
#             available_centers = np.array([centers_list[k][j] for k in available_idx])
#             available_weights = np.array([weights_list[k][j] for k in available_idx])

#             for i in range(center_dim):
#                 # Interpolate center component i
#                 interpolated_centers[j, i] = self.interpolate(available_locs, available_centers[:, i], query_loc)

#             # Interpolate weight
#             interpolated_weights[j] = self.interpolate(available_locs, available_weights, query_loc)

#         return interpolated_centers, interpolated_weights

# class GaussianProcessRBFParameters(GaussianProcess):
#     def interpolate_parameters(self, known_locs, centers_list, weights_list, query_loc):
#         """
#         Interpolate RBF centers and weights at query location using GP.
#         Only interpolate over available centers/weights at each position.
#         """
#         n_points = known_locs.shape[0]

#         max_centers = max(center.shape[0] for center in centers_list)
#         center_dim = centers_list[0].shape[1]

#         interpolated_centers = np.zeros((max_centers, center_dim))
#         interpolated_weights = np.zeros(max_centers)

#         for j in range(max_centers):
#             available_idx = [k for k in range(n_points) if centers_list[k].shape[0] > j]

#             if not available_idx:
#                 continue  # No data for this center

#             available_locs = known_locs[available_idx]
#             available_centers = np.array([centers_list[k][j] for k in available_idx])
#             available_weights = np.array([weights_list[k][j] for k in available_idx])

#             for i in range(center_dim):
#                 y_train = available_centers[:, i]
#                 self.fit(available_locs, y_train)
#                 interpolated_centers[j, i] = self.predict(query_loc[None, :])

#             y_train = available_weights
#             self.fit(available_locs, y_train)
#             interpolated_weights[j] = self.predict(query_loc[None, :])

#         return interpolated_centers, interpolated_weights


# if __name__ == "__main__":
#     # Example usage of Kriging
#     kriging = Kriging(sigma2=1.0, zeta=10.0)

#     known_locs = np.array([
#         [0.0, 0.0],
#         [10.0, 0.0],
#         [5.0, 10.0],
#         [7.0, 7.0]
#     ])
#     known_values = np.array([2.5, 3.0, 2.0, 2.8])
#     query_loc = np.array([5.0, 5.0])

#     estimate = kriging.interpolate(known_locs, known_values, query_loc)
#     print(f"[Kriging] Interpolated wind speed at {query_loc}: {estimate:.3f} m/s")

#     # Example usage of Gaussian Process
#     gp = GaussianProcess(sigma2=1.0, zeta=10.0, noise=1e-6)
#     gp.fit(known_locs, known_values)
#     y_pred = gp.predict(query_loc[None, :])
#     print(f"[GP] Predicted wind speed at {query_loc}: {y_pred[0]:.3f} m/s")

#     # Example for RBF parameter interpolation
#     centers_list = [
#         np.random.rand(5, 2),
#         np.random.rand(5, 2),
#         np.random.rand(5, 2),
#         np.random.rand(5, 2)
#     ]
#     weights_list = [
#         np.random.rand(5),
#         np.random.rand(5),
#         np.random.rand(5),
#         np.random.rand(5)
#     ]

#     # Kriging RBF Parameters
#     kriging_rbf = KrigingRBFParameters(sigma2=1.0, zeta=10.0)
#     centers_interp, weights_interp = kriging_rbf.interpolate_parameters(
#         known_locs, centers_list, weights_list, query_loc
#     )
#     print(f"[Kriging] Interpolated RBF centers at {query_loc}:\n{centers_interp}")
#     print(f"[Kriging] Interpolated RBF weights at {query_loc}:\n{weights_interp}")

#     # GP RBF Parameters
#     gp_rbf = GaussianProcessRBFParameters(sigma2=1.0, zeta=10.0, noise=1e-6)
#     centers_interp_gp, weights_interp_gp = gp_rbf.interpolate_parameters(
#         known_locs, centers_list, weights_list, query_loc
#     )
#     print(f"[GP] Interpolated RBF centers at {query_loc}:\n{centers_interp_gp}")
#     print(f"[GP] Interpolated RBF weights at {query_loc}:\n{weights_interp_gp}")




import numpy as np

class GPInterpolator:
    def __init__(self, kernel_type='squared_exponential', gamma=1.0, noise_var=0.0):
        self.kernel_type = kernel_type
        self.gamma = gamma
        self.noise_var = noise_var  # σ_n^2

    def _kernel(self, r1, r2):
        dist = np.linalg.norm(r1 - r2)
        if self.kernel_type == 'squared_exponential':
            return np.exp(-self.gamma * dist ** 2)
        elif self.kernel_type == 'ornstein_uhlenbeck':
            return np.exp(-self.gamma * dist)
        else:
            raise ValueError("Unsupported kernel type")

    def _build_cov_matrix(self, known_locs, query_loc):
        k = len(known_locs)
        Sigma = np.zeros((k, k))
        for i in range(k):
            for j in range(k):
                Sigma[i, j] = self._kernel(known_locs[i], known_locs[j])

        k_star = np.array([self._kernel(query_loc, loc) for loc in known_locs])
        return Sigma, k_star

    def interpolate(self, known_locs, known_values, query_loc):
        """
        known_locs: (N, 3) array of spatial locations (e.g., x, y, z)
        known_values: (N,) array of scalar model outputs (e.g., wind forecast at each location)
        query_loc: (3,) array of the location to interpolate at
        """
        known_locs = np.array(known_locs)
        known_values = np.array(known_values)
        query_loc = np.array(query_loc)

        Sigma, k_star = self._build_cov_matrix(known_locs, query_loc)
        k = Sigma.shape[0]
        Sigma += self.noise_var * np.eye(k)

        try:
            L = np.linalg.cholesky(Sigma)
            alpha = np.linalg.solve(L.T, np.linalg.solve(L, known_values))
            interp_value = k_star @ alpha
        except np.linalg.LinAlgError:
            inv_Sigma = np.linalg.pinv(Sigma)
            interp_value = k_star @ inv_Sigma @ known_values

        return interp_value



# import numpy as np

# class GPInterpolator:
#     def __init__(self, kernel_type='squared_exponential', gamma=1.0, noise_var=0.0):
#         self.kernel_type = kernel_type
#         self.gamma = gamma
#         self.noise_var = noise_var

#     def _kernel(self, r1, r2):
#         dist = np.linalg.norm(r1 - r2)
#         if self.kernel_type == 'squared_exponential':
#             return np.exp(-self.gamma * dist ** 2)
#         elif self.kernel_type == 'ornstein_uhlenbeck':
#             return np.exp(-self.gamma * dist)
#         else:
#             raise ValueError("Unsupported kernel type")

#     def _kernel_grad(self, r, known_locs):
#         """
#         Gradient of k(r, r_i) w.r.t r, for Taylor expansion.
#         """
#         grads = []
#         for ri in known_locs:
#             diff = r - ri
#             dist_sq = np.dot(diff, diff)
#             if self.kernel_type == 'squared_exponential':
#                 k_val = np.exp(-self.gamma * dist_sq)
#                 grad = -2 * self.gamma * k_val * diff
#             else:
#                 raise NotImplementedError("Grad only supported for squared_exponential")
#             grads.append(grad)
#         return np.stack(grads, axis=0)  # shape: (N, D)

#     def _build_cov_matrix(self, known_locs, query_loc=None):
#         k = len(known_locs)
#         Sigma = np.zeros((k, k))
#         for i in range(k):
#             for j in range(k):
#                 Sigma[i, j] = self._kernel(known_locs[i], known_locs[j])
#         k_star = None
#         if query_loc is not None:
#             k_star = np.array([self._kernel(query_loc, loc) for loc in known_locs])
#         return Sigma, k_star

#     def interpolate(self, known_locs, known_values, query_mean, method='standard',
#                     input_cov=None, n_samples=1000, alpha=1e-3, beta=2.0, kappa=0.0):
#         """
#         method: 'standard' | 'taylor' | 'ut' | 'monte_carlo'
#         input_cov: Covariance of query point (for taylor/ut/monte_carlo)
#         """
#         known_locs = np.array(known_locs)
#         known_values = np.array(known_values)
#         query_mean = np.array(query_mean)
#         D = query_mean.shape[0]
#         N = known_locs.shape[0]

#         Sigma, _ = self._build_cov_matrix(known_locs)
#         Sigma += self.noise_var * np.eye(N)
#         inv_Sigma = np.linalg.pinv(Sigma)

#         if method == 'standard':
#             _, k_star = self._build_cov_matrix(known_locs, query_mean)
#             return k_star @ inv_Sigma @ known_values

#         elif method == 'taylor':
#             if input_cov is None:
#                 raise ValueError("input_cov is required for Taylor method")
#             k_star = np.array([self._kernel(query_mean, loc) for loc in known_locs])
#             grad_k = self._kernel_grad(query_mean, known_locs)  # shape: (N, D)
#             correction = np.einsum('ni,ij,nj->n', grad_k, input_cov, grad_k)  # (N,)
#             return (k_star + 0.5 * correction) @ inv_Sigma @ known_values

#         elif method == 'ut':
#             if input_cov is None:
#                 raise ValueError("input_cov is required for Unscented Transform")
#             lambda_ = alpha ** 2 * (D + kappa) - D
#             sigma_points = [query_mean]
#             sqrt_mat = np.linalg.cholesky((D + lambda_) * input_cov)
#             for i in range(D):
#                 sigma_points.append(query_mean + sqrt_mat[:, i])
#                 sigma_points.append(query_mean - sqrt_mat[:, i])
#             sigma_points = np.array(sigma_points)

#             w_m = np.full(2 * D + 1, 1 / (2 * (D + lambda_)))
#             w_m[0] = lambda_ / (D + lambda_)
#             w_c = np.copy(w_m)
#             w_c[0] += 1 - alpha ** 2 + beta

#             preds = []
#             for pt in sigma_points:
#                 k_star = np.array([self._kernel(pt, loc) for loc in known_locs])
#                 preds.append(k_star @ inv_Sigma @ known_values)
#             preds = np.array(preds)
#             return np.sum(w_m * preds)

#         elif method == 'monte_carlo':
#             if input_cov is None:
#                 raise ValueError("input_cov is required for Monte Carlo")
#             samples = np.random.multivariate_normal(query_mean, input_cov, size=n_samples)
#             preds = []
#             for pt in samples:
#                 k_star = np.array([self._kernel(pt, loc) for loc in known_locs])
#                 preds.append(k_star @ inv_Sigma @ known_values)
#             return np.mean(preds)

#         else:
#             raise ValueError("Invalid interpolation method")



class GPParameterInterpolator:
    def __init__(self, kernel_type='squared_exponential', gamma=1.0, noise_var=0.0):
        self.kernel_type = kernel_type
        self.gamma = gamma
        self.noise_var = noise_var  # σ²ₙ

    def _kernel(self, r1, r2):
        dist = np.linalg.norm(r1 - r2)
        if self.kernel_type == 'squared_exponential':
            return np.exp(-self.gamma * dist ** 2)
        elif self.kernel_type == 'ornstein_uhlenbeck':
            return np.exp(-self.gamma * dist)
        else:
            raise ValueError("Unsupported kernel type")

    def _build_cov_matrix(self, locs, query_loc):
        k = len(locs)
        Sigma = np.zeros((k, k))
        k_star = np.zeros(k)

        for i in range(k):
            for j in range(k):
                Sigma[i, j] = self._kernel(locs[i], locs[j])
            k_star[i] = self._kernel(query_loc, locs[i])

        return Sigma, k_star

    def interpolate(self, known_locs, known_params, query_loc):
        """
        known_locs: (K, 3) array of locations where model parameters are known
        known_params: (K, D) array of model parameter vectors at each location
        query_loc: (3,) location to interpolate model parameters at

        Returns:
            interpolated_params: (D,) interpolated model parameters at query_loc
        """
        known_locs = np.array(known_locs)
        known_params = np.array(known_params)
        query_loc = np.array(query_loc)

        Sigma, k_star = self._build_cov_matrix(known_locs, query_loc)
        K = Sigma.shape[0]
        Sigma += self.noise_var * np.eye(K)

        try:
            inv_Sigma = np.linalg.inv(Sigma)
        except np.linalg.LinAlgError:
            inv_Sigma = np.linalg.pinv(Sigma)

        # Interpolate each parameter dimension separately
        interpolated_params = np.zeros(known_params.shape[1])
        for d in range(known_params.shape[1]):
            θ_d = known_params[:, d]
            interpolated_params[d] = np.dot(k_star, inv_Sigma @ θ_d)

        return interpolated_params
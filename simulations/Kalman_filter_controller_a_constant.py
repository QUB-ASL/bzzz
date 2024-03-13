import numpy as np
import matplotlib.pyplot as plt

# System parameters
T_s = 0.1  # Sampling time
g = 9.81   # Gravitational acceleration
mass = 3000

# Let tau be the % throttle
# lift (g) = alpha_0 * tau  + beta_0
alpha_0 = 8654
beta_0  = -797.67

# acc (m/s^2) = alpha * tau + beta
beta_est = beta_0 / mass - g
alpha_est = alpha_0 / mass


# Equilibrium throttle
tau_eq = -beta_est / alpha_est
tau_t = tau_eq  # throttle signal, will vary for real application  

# Measurement matrix C
C = np.array([
    [1, 0, 0, 1, 0],  # Barometer measurement with bias
    [1, 0, 0, 0, 1],  # ToF measurement with bias
    [1, 0, 0, 0, 0]   # GPS measurement without bias
])

# Process noise covariance matrix Q
sigma_z, sigma_v, sigma_beta = 0.05, 0.03, 0.1
sigma_d_bar, sigma_d_ToF = 0.1, 0.1  
Q = np.diag([sigma_z**2, sigma_v**2, T_s*sigma_beta**2, sigma_d_bar**2, sigma_d_ToF**2])

# Measurement noise covariance matrix R
sigma_barom, sigma_gps, sigmAoF = 0.15 * T_s, 0.075 * T_s, 0.01 * T_s
R = np.diag([sigma_barom**2, sigma_gps**2, sigmAoF**2])

# Initial conditions
Sigma_pred = 1000 * np.eye(5)
x_pred = np.array([1, 0, beta_est, 0, 0]).reshape(-1, 1)  # Initial predicted state with biases
x_true = np.array([1, 0, beta_est, 0, 0]).reshape(-1, 1)  # Initial true state with biases

# Simulation parameters
t_sim = 200
x_true_cache = np.zeros((5, t_sim))
x_meas_cache = np.zeros((5, t_sim))

def dynamics(x, tau=tau_eq):
    """ Simulate the system dynamics """
    # State transition matrix A
    A = np.array([
            [1, T_s, 0, 0, 0], 
            [0, 1, T_s, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1]
            ])
    
    d = np.array([
        [0],
        [T_s*alpha_est*tau],
        [0],
        [0],
        [0]
    ])
    w = np.random.multivariate_normal(np.zeros(5), Q).reshape(-1, 1)
    x_next = A @ x + d + w  # Dynamics include the effect of tau_t, alpha, and beta
    return x_next

def prediction_step(tau=tau_eq):
    A = np.array([
            [1, T_s, 0, 0, 0], 
            [0, 1, T_s, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1]
            ])
    
    d = np.array([
        [0],
        [T_s*alpha_est*tau],
        [0],
        [0],
        [0]
    ])
    x_pred = A @ x_meas + d 
    Sigma_pred = A @ Sigma_meas @ A.T + Q
    return x_pred, Sigma_pred


def measurement_update(y):
    M = C @ Sigma_pred @ C.T + R
    x_meas = x_pred +  (Sigma_pred @ C.T) @ np.linalg.solve(M, y - C @ x_pred)
    F = np.linalg.solve(M, C @ Sigma_pred)    
    Sigma_meas = Sigma_pred - (Sigma_pred @ C.T) @ F
    return x_meas, Sigma_meas

def output(x):
    """ Simulate the system output"""
    v = np.random.multivariate_normal(np.zeros(3), R).reshape(-1, 1)  
    y = C @ x + v  
    return y



tau = tau_eq


# Main simulation loop
for t in range(t_sim):
    
    # Simulate sensor measurements
    y = output(x_true)
    
    # if t > 30:
    #     y[1] += 0.5

    # Kalman Filter: Measurement update
    x_meas, Sigma_meas = measurement_update(y)
    
    
    tau = tau_eq
    #print(x_meas[3])

    # Kalman Filter: Time update
    x_pred, Sigma_pred = prediction_step(tau)
    
    # Simulate system dynamics
    x_true = dynamics(x_true, tau)

    # Store values for plotting
    x_true_cache[:, t] = x_true.ravel()
    x_meas_cache[:, t] = x_meas.ravel()

#Plot results
fig, ax = plt.subplots(nrows=2, ncols=3)

ax[0,0].plot(x_true_cache[2, :], label='True Beta')
ax[0,0].plot(x_meas_cache[2, :], label='Estimated Beta')
ax[0,0].legend()


ax[0, 1].plot(x_true_cache[1, :], label='True velocity')
ax[0, 1].plot(x_meas_cache[1, :], label='Estimated velocity')
ax[0, 1].legend()

ax[0, 2].plot(x_true_cache[0, :], label='True altitude')
ax[0, 2].plot(x_meas_cache[0, :], label='Estimated altitdue')
ax[0, 2].legend()

ax[1, 0].plot(x_true_cache[3, :], label='True bias Barom')
ax[1, 0].plot(x_meas_cache[3, :], label='Estimated bias Barom')
ax[1, 0].legend()

ax[1, 1].plot(x_true_cache[4, :], label='True bias ToF')
ax[1, 1].plot(x_meas_cache[4, :], label='Estimated bias ToF')
ax[1, 1].legend()


ax[1, 2].plot(-x_true_cache[2, :]/alpha_est, label='tau eq')
ax[1, 2].legend()
plt.show()

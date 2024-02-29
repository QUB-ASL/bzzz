"""
please see /whitepapers/kalmanfilter/kalmanfilter.pdf for source equations
first we will begin to implement a simulator for kalman filter using the equations found in this document

"""

import numpy as np
import matplotlib.pyplot as plt

# System parameters
Ts = 1.0  # Sampling time, s
g = 9.81  # Gravitational acceleration, m/s^2

# Initial state vector
x_true = np.array([0, 0, 0.1, -g, 0, 0]).reshape(-1, 1)  # Initial true state

# State transition matrix (A)
A = np.eye(6)
A[0, 1] = Ts  # Altitude depends on velocity
A[1, 2] = Ts  # Velocity depends on alpha
A[1, 3] = Ts  # Velocity depends on beta

# Process noise covariance (Q)
Q = np.diag([0.01, 0.01, 0.001, 0.001, 0.001, 0.001])

# Measurement matrices (C) for each sensor
C_bar = np.array([1, 0, 0, 0, 1, 0])  # Barometer measures altitude and bias
C_gps = np.array([1, 0, 0, 0, 0, 0])  # GPS measures altitude
C_tof = np.array([1, 0, 0, 0, 0, 1])  # ToF measures altitude and bias

# Measurement noise covariance (R) for each sensor
R_bar = 0.2
R_gps = 0.5
R_tof = 0.1

# Initial estimates
x_est = np.zeros((6, 1))  # Initial estimate for the state
P_est = np.eye(6)  # Initial estimate for the state covariance

# Number of time steps
n_steps = 100

# Storage for plotting
true_states = np.zeros((6, n_steps))
est_states = np.zeros((6, n_steps))
meas_states = np.zeros((3, n_steps))  # Measurements from each sensor

for t in range(n_steps):
    # Simulate the system (True dynamics)
    x_true = A @ x_true + np.random.multivariate_normal(np.zeros(6), Q).reshape(-1, 1)

    # Generate measurements
    y_bar = C_bar @ x_true + np.random.normal(0, R_bar)
    y_gps = C_gps @ x_true + np.random.normal(0, R_gps)
    y_tof = C_tof @ x_true + np.random.normal(0, R_tof)

    # Extract scalar values from measurements if they're array-like
       # Extract scalar values from measurements if they're array-like
    y_bar_scalar = y_bar.item() if isinstance(y_bar, np.ndarray) and y_bar.size == 1 else y_bar
    y_gps_scalar = y_gps.item() if isinstance(y_gps, np.ndarray) and y_gps.size == 1 else y_gps
    y_tof_scalar = y_tof.item() if isinstance(y_tof, np.ndarray) and y_tof.size == 1 else y_tof

    # Assign scalar measurements for this time step
    meas_states[:, t] = [y_bar_scalar, y_gps_scalar, y_tof_scalar]

    # Kalman Filter: Time Update (Prediction)
    x_pred = A @ x_est
    P_pred = A @ P_est @ A.T + Q

    # Kalman Filter: Measurement Update (Correction) for each sensor
    for C, y, R in zip([C_bar, C_gps, C_tof], [y_bar_scalar, y_gps_scalar, y_tof_scalar], [R_bar, R_gps, R_tof]):
        C = C.reshape(1, -1)  # Ensure C is a row vector
        K = P_pred @ C.T @ np.linalg.inv(C @ P_pred @ C.T + R)
        x_est = x_pred + K @ (y - C @ x_pred)
        P_est = (np.eye(6) - K @ C) @ P_pred

    # Store states for plotting
    true_states[:, t] = x_true.flatten()
    est_states[:, t] = x_est.flatten()

# Plotting
plt.figure(figsize=(12, 8))

# Altitude plot
plt.subplot(2, 1, 1)
plt.plot(true_states[0, :], label='True Altitude')
plt.plot(meas_states[0, :], label='Barometer', linestyle=':', color='orange')
plt.plot(meas_states[1, :], label='GPS', linesty
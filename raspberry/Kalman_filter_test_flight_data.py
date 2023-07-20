from matplotlib import pyplot as plt
import numpy as np
import pandas as pd


from simulations.altitude_dynamics import AltitudeDynamics
from estimators.altitude_Kalman_filter import KalmanFilter



# load collected flight data
flight_data = pd.read_csv("total_flight_data.csv", header=None).to_numpy(copy=True)
Tref_t = (flight_data[:, 1] - 1000)/1000
altitude_measurements_t = flight_data[:, 5]

num_data_points_collected = len(Tref_t)
sampling_frequency = 50
sampling_time = 1./sampling_frequency
time_stamps = [i*sampling_time for i in range(num_data_points_collected)]

kf = KalmanFilter(sampling_frequency=sampling_frequency, initial_Tt=Tref_t[0], x_tilde_0=np.array([[0], [0], [-0.001], [1.534]]), cache_values=True)

y_t = np.zeros(num_data_points_collected)
for i in range(num_data_points_collected):
    y_t[i] = altitude_measurements_t[i]
    kf.run(Tref_t[i], y_t[i]).reshape(4, )


x_hat_t, _ = kf.MU_cache()
x_hat_t = np.array(x_hat_t).reshape((num_data_points_collected, 4))
print("alpha hat = %f"%x_hat_t[-1, 2], "\nc hat = %f"%x_hat_t[-1, 3])

fig, sub_plts = plt.subplots(2)

sub_plts[0].plot(time_stamps, x_hat_t[:, 0])
sub_plts[0].plot(time_stamps, y_t)
sub_plts[0].legend([r"$\hat{z}_t$", r"$y_t$"])
sub_plts[0].set_xlabel("time s")
sub_plts[0].set_ylabel("altitude m")
sub_plts[0].grid(True)

sub_plts[1].plot(time_stamps, x_hat_t[:, 2])
sub_plts[1].plot(time_stamps, x_hat_t[:, 3])
sub_plts[1].legend([r"$\hat{\alpha}_t$", r"$\hat{\beta}_t$"])
sub_plts[1].set_xlabel("time s")
sub_plts[1].set_ylabel("parameter estimates")
sub_plts[1].grid(True)
plt.show()

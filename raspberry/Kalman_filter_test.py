from matplotlib import pyplot as plt
import numpy as np

from simulations.altitude_dynamics import AltitudeDynamics
from estimators.altitude_Kalman_filter import KalmanFilter


num_data_points_collected = 100
sampling_frequency = 10
sampling_time = 1./sampling_frequency
time_stamps = [i*sampling_time for i in range(num_data_points_collected)]


# Simulate the dynamics and fake the measurement data for testing the least squares estimations
dynamics = AltitudeDynamics(sampling_time=sampling_time)
Tref_t = [20*np.sin(0.1*t) + 20*np.cos(1*t) for t in range(num_data_points_collected)]
for i in range(num_data_points_collected - 1):
    dynamics.simulate(Tref_t=Tref_t[i])


kf = KalmanFilter(initial_Tt=Tref_t[0], cache_values=True)

y_t = np.zeros(num_data_points_collected)
for i in range(num_data_points_collected):
    y_t[i] = dynamics.z[i] + np.random.normal(0, 0.1)
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

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd


from simulations.altitude_dynamics import AltitudeDynamics
from estimators.altitude_Kalman_filter import KalmanFilter



# load collected flight data
flight_data = pd.read_csv("testdata.csv", header=None).to_numpy(copy=True)
Tref_t = (flight_data[:, 1] - 1000)/850
altitude_measurements_t = flight_data[:, 5]/1000
acc_imu = flight_data[:, -1]

indices_of_actual_flight = altitude_measurements_t > 0.01

Tref_t = Tref_t[indices_of_actual_flight]
altitude_measurements_t = altitude_measurements_t[indices_of_actual_flight]
acc_imu = acc_imu[indices_of_actual_flight]

num_data_points_collected = len(Tref_t)
sampling_frequency = 50
sampling_time = 1./sampling_frequency
time_stamps = [i*sampling_time for i in range(num_data_points_collected)]

kf = KalmanFilter(sampling_frequency=sampling_frequency, initial_Tt=Tref_t[0], x_tilde_0=np.array([[0], [0], [3], [-2]]), cache_values=True)

y_t = np.zeros(num_data_points_collected)
for i in range(num_data_points_collected):
    y_t[i] = altitude_measurements_t[i]
    kf.run(Tref_t[i], y_t[i]).reshape(4, )


x_hat_t, _ = kf.MU_cache()
x_hat_t = np.array(x_hat_t).reshape((num_data_points_collected, 4))
print("alpha hat = %f"%x_hat_t[-1, 2], "\nc hat = %f"%x_hat_t[-1, 3])

fig, sub_plts = plt.subplots(4)

sub_plts[0].plot(time_stamps, x_hat_t[:, 0])
sub_plts[0].plot(time_stamps, y_t)
sub_plts[0].legend([r"$\hat{z}_t$", r"$y_t$"])
sub_plts[0].set_xlabel("time s")
sub_plts[0].set_ylabel("altitude m")
sub_plts[0].grid(True)

sub_plts[1].plot(time_stamps, x_hat_t[:, 2])
sub_plts[1].legend([r"$\hat{\alpha}_t$"])
sub_plts[1].set_xlabel("time s")
sub_plts[1].set_ylabel("parameter estimates")
sub_plts[1].grid(True)

sub_plts[2].plot(time_stamps, x_hat_t[:, 3])
sub_plts[2].legend([r"$\hat{\beta}_t$"])
sub_plts[2].set_xlabel("time s")
sub_plts[2].set_ylabel("parameter estimates")
sub_plts[2].grid(True)

sub_plts[3].plot(time_stamps, Tref_t)
sub_plts[3].set_xlabel("time s")
sub_plts[3].set_ylabel("Tref_t")
sub_plts[3].grid(True)

# delta_v_t1 = x_hat_t[1:, 1] - x_hat_t[:-1, 1]
# sub_plts.scatter(Tref_t[:-1], delta_v_t1)
# sub_plts.set_xlabel("Tref_t")
# sub_plts.set_ylabel("delta V")
# sub_plts.grid(True)

# acc = altitude_measurements_t[2:] - 2*altitude_measurements_t[1:-1] + altitude_measurements_t[:-2]
# sub_plts[0].scatter(Tref_t[:-2], acc)

# sub_plts[0].set_xlabel("Tref_t")
# sub_plts[0].set_ylabel("Acc a")
# sub_plts[0].grid(True)

# sub_plts[1].scatter(Tref_t, acc_imu)
# sub_plts[1].set_xlabel("Tref_t")
# sub_plts[1].set_ylabel("Acc a imu")
# sub_plts[1].grid(True)
plt.show()

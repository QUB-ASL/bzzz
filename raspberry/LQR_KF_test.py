from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from math import pi

from simulations.altitude_dynamics import AltitudeDynamics
from estimators.altitude_Kalman_filter import KalmanFilter
from controllers.altitude_LQR import LQR



# load collected flight data
flight_data = pd.read_csv("testdata.csv", header=None).to_numpy(copy=True)
Tref_t = (flight_data[:, 1] - 1000)/850
altitude_measurements_t = flight_data[:, 5]/1000
# altitude_measurements_t -= np.min(altitude_measurements_t)
pitch_measurements = flight_data[:, 3]
roll_measurements = flight_data[:, 4]
acc_imu = flight_data[:, -1]

indices_of_actual_flight = altitude_measurements_t > 0.0

Tref_t = Tref_t[indices_of_actual_flight]
altitude_measurements_t = altitude_measurements_t[indices_of_actual_flight]
pitch_measurements = pitch_measurements[indices_of_actual_flight]
roll_measurements = roll_measurements[indices_of_actual_flight]
acc_imu = acc_imu[indices_of_actual_flight]
time_stamps = flight_data[indices_of_actual_flight, 0] * 1e-9

num_data_points_collected = len(Tref_t)
sampling_frequency = 50
sampling_time = 1./sampling_frequency
# time_stamps = [i*sampling_time for i in range(num_data_points_collected)]

kf = KalmanFilter(sampling_frequency=sampling_frequency, initial_Tt=Tref_t[0], x_tilde_0=np.array([[0], [0], [10], [-9.81]]), P_0=np.diagflat([1, 1, 1, 0.01]), cache_values=True)
lqr = LQR(sampling_frequency=50, initial_alpha_t=10, initial_beta_t=-9.81)


y_t = np.zeros(num_data_points_collected)
throttle_ref_from_LQR = np.zeros(num_data_points_collected)
for i in range(num_data_points_collected):
    y_t[i] = altitude_measurements_t[i]
    x_est = kf.run(Tref_t[i], pitch_measurements[i], roll_measurements[i], y_t[i]).reshape(4, )
    z_hat = x_est[0]
    v_hat = x_est[1]
    alpha_hat = x_est[2]
    beta_hat = x_est[3]

    throttle_ref_from_LQR[i] = lqr.control_action(np.array([[z_hat], [v_hat]]), alpha_t=alpha_hat, beta_t=beta_hat, reference_altitude_mts=1, recalculate_dynamics=True)
    



x_hat_t, _ = kf.MU_cache()
x_hat_t = np.array(x_hat_t).reshape((num_data_points_collected, 4))
print("alpha hat = %f"%x_hat_t[-1, 2], "\nc hat = %f"%x_hat_t[-1, 3])

fig, sub_plts = plt.subplots(5)

idx_pl = 0
sub_plts[idx_pl].plot(time_stamps, x_hat_t[:, 0])
sub_plts[idx_pl].plot(time_stamps, y_t)
sub_plts[idx_pl].legend([r"$\hat{z}_t$", r"$y_t$"])
sub_plts[idx_pl].set_ylabel("altitude m")
sub_plts[idx_pl].grid(True)

idx_pl += 1
sub_plts[idx_pl].plot(time_stamps, x_hat_t[:, 2])
sub_plts[idx_pl].legend([r"$\hat{\alpha}_t$"])
sub_plts[idx_pl].set_ylabel("parameter estimates")
sub_plts[idx_pl].grid(True)

idx_pl += 1
sub_plts[idx_pl].plot(time_stamps, x_hat_t[:, 3])
sub_plts[idx_pl].legend([r"$\hat{\beta}_t$"])
sub_plts[idx_pl].set_ylabel("parameter estimates")
sub_plts[idx_pl].grid(True)

idx_pl += 1
sub_plts[idx_pl].plot(time_stamps, throttle_ref_from_LQR)
sub_plts[idx_pl].set_ylabel("T_LQR")
sub_plts[idx_pl].grid(True)


# sub_plts[2].plot(time_stamps, pitch_measurements*180/pi)
# sub_plts[2].plot(time_stamps, roll_measurements*180/pi)
# sub_plts[2].legend([r"pitch ", r"roll"])
# sub_plts[2].set_xlabel("time s")
# sub_plts[2].set_ylabel("angle m")
# sub_plts[2].grid(True)

# idx_pl += 1
# sub_plts[idx_pl].plot(time_stamps, Tref_t)
# sub_plts[idx_pl].set_ylabel("Tref (RC)")
# sub_plts[idx_pl].grid(True)


idx_pl += 1
sub_plts[idx_pl].plot(time_stamps, - x_hat_t[:, 3] / x_hat_t[:, 2])
sub_plts[idx_pl].plot(time_stamps, Tref_t)
sub_plts[idx_pl].set_ylabel("Tref (RC)")
sub_plts[idx_pl].grid(True)



sub_plts[idx_pl].set_xlabel("time s")
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

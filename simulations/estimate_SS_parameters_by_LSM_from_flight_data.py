# TODO: Documentation

import cvxpy as cp
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd


# load collected flight data
flight_data = pd.read_csv("total_flight_data.csv", header=None).to_numpy(copy=True)
Tref_t = flight_data[:, 1]
altitude = flight_data[:, 5]

indices_of_actual_flight = altitude > 50

Tref_t = (Tref_t[indices_of_actual_flight] - 1000)/1000
altitude = altitude[indices_of_actual_flight]

num_data_points_collected = len(Tref_t)
sampling_frequency = 50


sampling_time = 1./sampling_frequency
time_stamps = [i*sampling_time for i in range(num_data_points_collected)]


alpha_hat = cp.Variable(shape=(1), name="alpha_hat")
c_hat = cp.Variable(shape=(1), name="c_hat")
vz_hat_t = cp.Variable(shape=(num_data_points_collected), name="vz_hat_t")
z_hat_t = cp.Variable(shape=(num_data_points_collected), name="z_hat_t")

cost_function = 0
constraints = []

for t in range(num_data_points_collected - 1):
    output_error = np.random.normal(0, 1.5)
    process_error = np.random.normal(loc=0, scale=0.08*sampling_time, size=2)
    y = z_hat_t[t] + output_error
    cost_function += (y - altitude[t])**2
    cstr1 = z_hat_t[t + 1] - \
        (z_hat_t[t] + sampling_time * vz_hat_t[t]) + process_error[0]
    cstr2 = vz_hat_t[t + 1] - (vz_hat_t[t] + sampling_time *
                               (alpha_hat * Tref_t[t] + c_hat)) + process_error[1]
    constraints += [cstr1 == 0, cstr2 == 0]

least_squares_problem = cp.Problem(cp.Minimize(cost_function), constraints)
least_squares_problem.solve()

if least_squares_problem.status != "optimal":
    raise Exception(
        f"Problem solution failed - status: {least_squares_problem.status}")

print("alpha hat = %.3f" % alpha_hat.value, "\nc hat = %.3f" % c_hat.value)

fig, sub_plts = plt.subplots(2)
plt.rcParams["font.size"] = 16

sub_plts[0].grid(True)
sub_plts[0].plot(time_stamps, altitude)
sub_plts[0].plot(time_stamps, z_hat_t.value.T)
sub_plts[0].legend(["$z_t$", "$\hat{z}_t$"])
sub_plts[0].set_xlabel("time s")
sub_plts[0].set_ylabel("altitude m")

sub_plts[1].grid(True)
# sub_plts[1].plot(time_stamps, altitude)
sub_plts[1].plot(time_stamps, vz_hat_t.value.T)
sub_plts[1].legend([r"$v_{z, t}$", r"$\hat{v}_{z, t}$"])
sub_plts[1].set_xlabel("time s")
sub_plts[1].set_ylabel(r"velocity m/s")
plt.show()

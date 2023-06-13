#TODO: Documentation


from altitude_dynamics import AltitudeDynamics

import cvxpy as cp
from matplotlib import pyplot as plt
import numpy as np


num_data_points_collected = 1000
sampling_frequency = 10


sampling_time = 1./sampling_frequency
time_stamps = [i*sampling_time for i in range(num_data_points_collected)]

# Simulate the dynamics and fake the measurement data for testing the least squares estimations
dynamics = AltitudeDynamics(sampling_time=sampling_time)
Tref_t = 9.82
for i in range(num_data_points_collected - 1):
    dynamics.simulate(Tref_t=Tref_t)

alpha_hat = cp.Parameter(shape=(1), name="alpha_hat")
alpha_hat.value = np.array([1])
c_hat = cp.Variable(shape=(1), name="c_hat")
vz_hat_t = cp.Variable(shape=(num_data_points_collected), name="vz_hat_t")
z_hat_t = cp.Variable(shape=(num_data_points_collected), name="z_hat_t")

cost_function = 0
constraints = []

for t in range(num_data_points_collected - 1):
  cost_function += cp.norm2(z_hat_t[t] - dynamics.z[t])**2
  constraints += [z_hat_t[t + 1] == z_hat_t[t] + sampling_time*vz_hat_t[t], vz_hat_t[t + 1] == vz_hat_t[t] + sampling_time*(alpha_hat*Tref_t + c_hat)]


cost_function += cp.norm2(z_hat_t[-1] - dynamics.z[-1])**2
constraints += [z_hat_t[-1] == z_hat_t[-2] + sampling_time*vz_hat_t[-2], vz_hat_t[-1] == vz_hat_t[-2] + sampling_time*(alpha_hat*Tref_t + c_hat)]


least_squares_problem = cp.Problem(cp.Minimize(cost_function), constraints)
least_squares_problem.solve()

print(alpha_hat.value, c_hat.value)

_, sub_plts = plt.subplots(2, 2)

sub_plts[0, 0].plot(time_stamps, dynamics.z)
sub_plts[0, 1].plot(time_stamps, z_hat_t.value.T)
sub_plts[1, 0].plot(time_stamps, dynamics.vz)
sub_plts[1, 1].plot(time_stamps, vz_hat_t.value.T)
plt.show()


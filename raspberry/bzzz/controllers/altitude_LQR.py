# TODO: Documentation
import numpy as np
from numpy.linalg import pinv
import control as ctrl

class LQR:
    def __init__(self, sampling_frequency = 10, initial_alpha_t = 0, initial_beta_t = 0) -> None:
        self.__fs = sampling_frequency
        self.__Ts = 1./sampling_frequency


        self.__alpha_t = initial_alpha_t
        self.__beta_t = initial_beta_t
        self.__A = np.array([
            [1, self.__Ts],
            [0, 1]
        ])
        self.__B_t = np.array([
            [0.5*(self.__Ts**2)*self.__alpha_t],
            [self.__Ts*self.__alpha_t]
        ])
        self.__C = np.array([[1, 0]])
        self.__d_t = np.array([
            [0.5*(self.__Ts**2)*self.__beta_t],
            [self.__Ts*self.__beta_t]
        ])


        self.__x_and_u_bar = np.zeros((3, 1))
        self.__reference_tracker_dynamics = np.zeros((self.__A.shape[0] + self.__C.shape[0], self.__A.shape[1] + self.__B_t.shape[1]), dtype=np.float64)
        self.__reference_tracker_matrix = np.zeros((3, 1))

        self.__Q = np.array([
            [100, 0],
            [0, 2]
        ])
        self.__R = np.array([[10]])
        self.__kappa = np.zeros((1, 2))

        self.__identity_mat_2_2 = np.eye(2, 2)

    def __recalculate_dynamics(self, alpha_t, beta_t):
        self.__alpha_t = alpha_t
        self.__beta_t = beta_t

        self.__A = np.array([
            [1, self.__Ts],
            [0, 1]
        ])
        print(f"alpha = {alpha_t}")
        self.__B_t = np.array([
            [0.5*(self.__Ts**2)*self.__alpha_t],
            [self.__Ts*self.__alpha_t]
        ])
        self.__C = np.array([[1, 0]])
        self.__d_t = np.array([
            [0.5*(self.__Ts**2)*self.__beta_t],
            [self.__Ts*self.__beta_t]
        ])

    def __recalculate_reference_tracker_dynamics_and_matrix(self, reference_altitude_mts):
        print(self.__B_t.shape)
        self.__reference_tracker_dynamics[:self.__A.shape[0], :self.__A.shape[1]] = self.__A - self.__identity_mat_2_2
        self.__reference_tracker_dynamics[:self.__A.shape[0], self.__A.shape[1]:] = self.__B_t
        self.__reference_tracker_dynamics[self.__A.shape[0]:, :self.__A.shape[1]] = self.__C
        self.__reference_tracker_matrix[:2, :] = -np.copy(self.__d_t)
        self.__reference_tracker_matrix[2, :] = reference_altitude_mts

    def __calculate_x_and_u_bar(self):
        self.__x_and_u_bar = pinv(self.__reference_tracker_dynamics)@self.__reference_tracker_matrix

    def __calculate_stabilising_gain(self):
        _, _, kappa = ctrl.dare(self.__A, self.__B_t, self.__Q, self.__R)
        self.__kappa[:, :] = -np.copy(kappa)

    def control_action(self, current_states_z_and_vz: np.array, alpha_t = 0, beta_t = 0, reference_altitude_mts = 1, recalculate_dynamics = False):
        if recalculate_dynamics:
            self.__recalculate_dynamics(alpha_t=alpha_t, beta_t=beta_t)
            self.__recalculate_reference_tracker_dynamics_and_matrix(reference_altitude_mts=reference_altitude_mts)
            self.__calculate_x_and_u_bar()
            self.__calculate_stabilising_gain()
        return self.__kappa@(current_states_z_and_vz - self.__x_and_u_bar[:2, :]) + self.__x_and_u_bar[2, :]
    


if __name__ == "__main__":
    lqr = LQR(initial_alpha_t=1, initial_beta_t=-9.81)
    print(lqr.control_action(current_states_z_and_vz=np.array([[2], [1]]), alpha_t=1, beta_t=-9.81, reference_altitude_mts=1, recalculate_dynamics=True))


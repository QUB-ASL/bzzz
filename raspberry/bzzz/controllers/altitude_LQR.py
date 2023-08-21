# Imports
import numpy as np
import control as ctrl
from math import cos

class LQR:
    def __init__(self, sampling_frequency = 10, initial_alpha_t = 0, initial_beta_t = 0):
        # sampling frequency
        self.__fs = sampling_frequency
        self.__Ts = 1./sampling_frequency

        # vertical accleration parameters 
        self.__alpha_t = initial_alpha_t
        self.__beta_t = initial_beta_t

        # system dynamics
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

        # reference tracker parameters
        self.__x_and_u_bar = np.zeros((3, 1))  # equilibrium points "The hover estimate"
        self.__reference_tracker_dynamics = np.zeros((self.__A.shape[0] + self.__C.shape[0], self.__A.shape[1] + self.__B_t.shape[1]), dtype=np.float64)
        self.__reference_tracker_matrix = np.zeros((3, 1))

        # LQR matrices
        self.__Q = np.eye(2)
        self.__R = np.array([[100]])
        self.__kappa = np.zeros((1, 2))  # pre-allocation for LQR gain

        self.__identity_mat_2_2 = np.eye(2, 2)

    def set_Q_and_R_matrix_gains(self, Q11, Q22, R):
        """Change Q and R matrices of LQR

        :param Q11: Q gain of matrix position (1, 1) or index (0, 0)
        :param Q22: Q gain of matrix position (2, 2) or index (1, 1)
        :param R: R gain of LQR
        """
        self.__Q[0, 0] = Q11
        self.__Q[1, 1] = Q22
        self.__R[0, 0] = R

    def __set_kappa_11_and_12(self, k11, k12):
        """Manually set feedback gain matrix instead of using LQR

        :param k11: Gain of matrix position (1, 1) or index (0, 0)
        :param k12: Gain of matrix position (1, 2) or index (0, 1)
        """
        if k11 != None:
            self.__kappa[0, 0] = k11
        if k12 != None:
            self.__kappa[0, 1] = k12

    def __recalculate_dynamics(self, alpha_t, beta_t, pitch_rad=0, roll_rad=0):
        """Update alpha_t, beta_t, drone pitch_rad and roll_rad, and recalculate the system dynamics (A, B, C, and D matrices).

        :param alpha_t: vertical accleration parameter alpha
        :param beta_t: vertical accleration parameter beta
        :param pitch_rad: drone's current pitch in radians, defaults to 0
        :param roll_rad: drone's current roll in radians, defaults to 0
        """

        # throttle multiplication factor
        # NOTE: the actual equation is 
        # a_z_global_frame = cos(pitch) * cos(roll) * a_z_local_frame
        # but we know that, a_z_local_frame = alpha * Tref + beta
        # then, a_z_global_frame = cos(pitch) * cos(roll) * (alpha * Tref + beta)
        # => a_z_global_frame = cos(pitch) * cos(roll) * alpha * Tref + cos(pitch) * cos(roll) * beta
        # let k_Tref = cos(pitch) * cos(roll)
        # then, a_z_global_frame = (k_Tref * alpha) * Tref + (k_Tref * beta)
        k_Tref = cos(pitch_rad) * cos(roll_rad)

        # update alpha and beta
        self.__alpha_t = alpha_t * k_Tref
        self.__beta_t = beta_t * k_Tref

        # update dynamics
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

    def __update_x_and_u_bar(self, reference_altitude_mts):
        """update the equilibrium points x_bar and u_bar.

        :param reference_altitude_mts: Reference altitude in meters
        """
        # update the quilibrium points, this solution is analytically obtained and so doesn't require finding a matrix inverse everytime
        self.__x_and_u_bar[0, 0] = reference_altitude_mts
        self.__x_and_u_bar[1, 0] = 0
        self.__x_and_u_bar[2, 0] = -self.__beta_t/self.__alpha_t

    def __calculate_stabilising_gain(self):
        """Calculate the stabilising feedback gain using LQR method, call this function whenever the system dynamics are updated 
        """
        _, _, kappa = ctrl.dare(self.__A, self.__B_t, self.__Q, self.__R)
        self.__kappa[:, :] = -np.copy(kappa)

    def control_action(self, current_states_z_and_vz: np.array, alpha_t = 0, beta_t = 0, reference_altitude_mts = 1, recalculate_dynamics = False, pitch_rad=0, roll_rad=0, k11=None, k12=None):
        """Calculate and return the normalized control action

        :param current_states_z_and_vz: current states of altitude in m and velocity in m/s in a 2x1 numpy array
        :param alpha_t: vertical accleration parameter alpha, defaults to 0
        :param beta_t: vertical accleration parameter beta, defaults to 0
        :param reference_altitude_mts: reference altitude in mts, defaults to 1
        :param recalculate_dynamics: True to update and recalulate system dynamics, defaults to False
        :param pitch_rad: current drone pitch in radians, defaults to 0
        :param roll_rad: current drone roll in radians, defaults to 0
        :param k11: if not None, overwrites the stabilising gain of kappa at matrix position (1, 1) to given value, defaults to None
        :param k12:  if not None, overwrites the stabilising gain of kappa at matrix position (1, 2) to given value, defaults to None
        :return: Throttle command in percentage in a numpy 1x1x1 matrix
        """
        if recalculate_dynamics:
            self.__recalculate_dynamics(alpha_t=alpha_t, beta_t=beta_t, pitch_rad=pitch_rad, roll_rad=roll_rad)
            self.__update_x_and_u_bar(reference_altitude_mts=reference_altitude_mts)
            if k11 == None or k12 == None:
                self.__calculate_stabilising_gain()
        self.__set_kappa_11_and_12(k11, k12)
        return self.__kappa@(current_states_z_and_vz - self.__x_and_u_bar[:2, :]) + self.__x_and_u_bar[2, :]
    


# test script
if __name__ == "__main__":
    lqr = LQR(initial_alpha_t=1, initial_beta_t=-9.81)
    print(lqr.control_action(current_states_z_and_vz=np.array([[2], [1]]), alpha_t=1, beta_t=-9.81, reference_altitude_mts=1, recalculate_dynamics=True))


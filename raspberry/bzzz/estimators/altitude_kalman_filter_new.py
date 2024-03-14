import numpy as np
import math

class KalmanFilter:
    """
    Kalman Filter for altitude hold parameters estimation.
    The states are now x = [Altitude in m, Velocity along z-axis in m/s, alpha, beta, bias_barom, bias_ToF].
    Alpha and beta are parameters that relate throttle reference percentage with vertical acceleration as follows,
    ===> a_z = alpha * Throttle_reference_percentage_along_z + beta.
    The Throttle_reference_percentage_along_z is given by Throttle_reference_percentage * cos(current_drone_pitch_rad) * cos(current_drone_roll_rad).
    """
    def __init__(self,
                 sampling_frequency=10,
                 initial_Tt=0.,
                 x_tilde_0=np.zeros((6, 1)),
                 P_0=np.eye(6)*100,
                 cache_values=False,
                 overwrite_x_MU=None,
                 overwrite_sigma_MU=None):
        """
        Constructor for the Kalman Filter.

        :param sampling_frequency: KF sampling frequency, defaults to 10.
        :param initial_Tt: Initial throttle reference to the system, defaults to 0.
        :param x_tilde_0: Initial conditions; initial state guess for the KF, now defaults to np.zeros((6, 1)) to accommodate the expanded state vector.
        :param P_0: Initial conditions: initial state guess variance, now defaults to np.eye(6)*100 to match the expanded state vector.
        :param cache_values: Enables caching KF values if True, defaults to False.
        """
        self.__fs = sampling_frequency
        self.__Ts = 1/self.__fs
        self.__is_yt_not_nan = True

        # Normalized Throttle reference, range [0, 1]
        self.__Tt = initial_Tt

        # System dynamics
        self.__At = self.__update_At()

        # Measurement matrix, adjusted to include GPS and sensor biases for Barometer and ToF.
        self.__C = np.array([
            [1, 0, 0, 0, 1, 0],  # Barometer measurement with bias
            [1, 0, 0, 0, 0, 1],  # ToF measurement without bias
            [1, 0, 0, 0, 0, 0]   # GPS measurement without bias
        ])

        # Process noise, adjusted for the expanded state vector.
        self.__Q = np.diag([1e-4, 1, 5, 1e-3, (0.25/3)**2, 0.02**2])

        # Measurement noise, adjusted to include noises for Barometer, ToF, and GPS.
        self.__R = np.diag([0.25**2, 0.01**2, 0.075**2])

        # Initial conditions
        self.__x_hat_0_minus1 = x_tilde_0
        self.__sigma_0_minus1 = P_0

        # Measurement update
        self.__x_MU = overwrite_x_MU
        self.__sigma_MU = overwrite_sigma_MU

        # Time update
        self.__x_TU = x_tilde_0
        self.__sigma_TU = P_0

        self.__cache_values = cache_values

        # Caches for measurement update and time update values
        self.__x_MU_cache = []
        self.__sigma_MU_cache = []
        self.__x_TU_cache = []
        self.__sigma_TU_cache = []

        # Cache first time update values
        self.__cache_TU_values()

    def __cache_MU_values(self):
        if self.__cache_values:
            self.__x_MU_cache.append(self.__x_MU)
            self.__sigma_MU_cache.append(self.__sigma_MU)

    def __cache_TU_values(self):
        if self.__cache_values:                
            self.__x_TU_cache.append(self.__x_TU)
            self.__sigma_TU_cache.append(self.__sigma_TU)

    def __update_At(self):
        """
        Update the state transition matrix At to accommodate the expanded state vector,
        including the biases for the Barometer and ToF sensors as constant terms.
        """
        self.__At = np.array([
            [1, self.__Ts,0, 0, 0, 0],
            [0, 1, self.__Ts*self.__Tt, self.__Ts, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1]
        ])

    def __update_Tt(self, Tt, pitch_rad, roll_rad):
        """
        Update the normalized throttle reference based on the current pitch and roll of the drone.
        """
        self.__Tt = math.cos(pitch_rad) * math.cos(roll_rad) * float(Tt)

    def measurement_update_cache(self):
        """returns Measurement update cache data.

        :return: list of measurement update cache data.
        """
        return self.__x_MU_cache, self.__sigma_MU_cache

    def time_update_cache(self):
        """returns Time update cache data.

        :return: list of time update cache data.
        """
        return self.__x_TU_cache, self.__sigma_TU_cache

    def __measurement_update(self,
                             y_t,
                             pitch_rad=0.,
                             roll_rad=0.):
        """Does measurement update step of the Kalman filter.

        :param y_t: Current altitude measurement.
        :param pitch_rad: current drone pitch in radians, defaults to 0.
        :param roll_rad: current drone roll in radians, defaults to 0.
        """
        # NOTE: The below line is added new and untested
        y_t = y_t * math.cos(pitch_rad) * math.cos(roll_rad)
        # this is just a number
        the_inv = self.__C@self.__sigma_TU@self.__C.T + self.__R
        the_inv = 1/the_inv
        temp = the_inv*self.__sigma_TU@self.__C.T
        self.__x_MU = self.__x_TU + temp@(y_t - self.__C@self.__x_TU)
        self.__sigma_MU = self.__sigma_TU - temp@self.__C@self.__sigma_TU
        self.__cache_MU_values()

    def __time_update(self):
        """Does time update step of the kalman filter.
        """
        self.__x_TU = self.__At@self.__x_MU
        self.__sigma_TU = self.__At@self.__sigma_MU@self.__At.T + self.__Q
        self.__cache_TU_values()

    def reset(self):
        """reset the kalman filter velocity estimate.
        NOTE: only call this if the drone is close to ground and/ or the system dynamics are altered.
        """
        self.__x_MU[1, 0] = 0.

    def update(self, Tt, pitch_rad, roll_rad, y_t):
        """Runs the Kalman filter for one step

        :param Tt: Current normalized throttle reference.
        :param pitch_rad: Current drone pitch in radians.
        :param roll_rad: Current drone roll in radians.
        :param y_t: Current altitude measurement in meters.
        :return: State estimate.
        """
        # Check if altitude measurement is nan or outlier (which is indicated by -1/1000).
        self.__is_yt_not_nan = not (np.isnan(y_t) or y_t < 0)
        # Update the throttle reference.
        self.__update_Tt(Tt, pitch_rad, roll_rad)
        # update the system matrix At.
        self.__update_At()
        # only do the measurement update if a valid measurement is received.
        if self.__is_yt_not_nan:
            # Do the measurement update.
            self.__measurement_update(y_t, pitch_rad, roll_rad)
        self.__time_update()  # Do the time update.
        # return measurement update estimate if a valid measurement is received else reuturn time update estimate.
        return self.__x_MU if self.__is_yt_not_nan else self.__x_TU

# TODO: This file has incorrect documentation, fix it!
import numpy as np
import math


# NOTE: This model is based example shown here (https://am-press.github.io/posts/maths/kalman-6/#imperfect-knowledge-of-the-input).
class PositionKalmanFilter:
    def __init__(self, sampling_frequency=10, initial_Tt=0., initial_alpha_t=0., initial_input=np.zeros((2, 1)), x_tilde_0=np.zeros((4, 1)), P_0=np.eye(4, 4)*100, cache_values=False, overwrite_x_MU=None, overwrite_sigma_MU=None) -> None:
        # sampling frequency
        self.__fs = sampling_frequency
        self.__Ts = 1/self.__fs
        self.__is_yt_not_nan = True

        # Normalized Throttle reference, range [0, 1]
        self.__Tt = initial_Tt  # this is an element in state space matrices, not treated as input in this model
        self.__alpha_t = initial_alpha_t  # this is an element in state space matrices, not treated as input in this model
        self.__ut = initial_input  # This is the actual input to the system

        # System dynamics
        self.__At = np.array([
            [1, 0, self.__Ts, 0],
            [0, 1, 0, self.__Ts],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        self.__Bt = self.__update_Bt()
        self.__C = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])

        # Process noise
        self.__Q = np.diagflat([1e-1, 1e-1, 1e-1, 1e-1])
        # input measurement noise, the units are rad^2
        self.__N = np.diagflat([1e-4, 1e-4])
        # output measurement noise
        self.__R = np.diagflat([1e-1, 1e-1])

        # initial conditions
        self.__x_hat_0_minus1 = x_tilde_0
        self.__sigma_0_minus1 = P_0
        
        # Measurement update
        self.__x_MU = overwrite_x_MU
        self.__sigma_MU = overwrite_sigma_MU

        # Time update
        self.__x_TU = x_tilde_0
        self.__sigma_TU = P_0

        self.__cache_MU_values = lambda : ()
        self.__cache_TU_values = lambda : ()

        self.__cache_values = cache_values
        if cache_values:
            # Measurement update cache
            self.__x_MU_cache = []
            self.__sigma_MU_cache = []

            def cache_MU():
                self.__x_MU_cache.append(self.__x_MU)
                self.__sigma_MU_cache.append(self.__sigma_MU)

            self.__cache_MU_values = cache_MU

            # Time update cache
            self.__x_TU_cache = []
            self.__sigma_TU_cache = []

            def cache_TU():
                self.__x_TU_cache.append(self.__x_TU)
                self.__sigma_TU_cache.append(self.__sigma_TU)

            self.__cache_TU_values = cache_TU
            # cache first MU from above
            self.__cache_TU_values()

    def __update_Bt(self):
        """Update state matrix Bt. 
        NOTE: This function should be called whenever Tt and/ or alpha_t are updated.
        """
        k1_t = self.__Ts*self.__alpha_t*self.__Tt
        k2_t = 0.5*self.__Ts*k1_t

        self.__Bt = np.array([
            [k2_t, 0],
            [0, -k2_t],
            [k1_t, 0],
            [0, -k1_t]
        ])

    def __update_Tt(self, Tt):
        """Update the throttle reference.

        :param Tt: Current normalized throttle reference.
        """
        self.__Tt = float(Tt)

    def __update_alpha_t(self, alpha_t):
        """Update the vertical accleration parameter alpha.

        :param alpha_t: Current estimate of alpha from altitude KF.
        """
        self.__alpha_t = float(alpha_t)

    def __update_ut(self, pitch_rad, roll_rad, heading):
        """Update the vertical accleration parameter alpha.

        :param alpha_t: Current estimate of alpha from altitude KF.
        """
        sin_r = math.sin(roll_rad)
        sin_p = math.sin(pitch_rad)
        self.__ut[0, 0] = math.sin(roll_rad)
        self.__ut[1, 0] = math.sin(pitch_rad)

    def MU_cache(self):
        """returns Measurement update cache data.

        :return: list of measurement update cache data.
        """
        return self.__x_MU_cache, self.__sigma_MU_cache
    
    def TU_cache(self):
        """returns Time update cache data.

        :return: list of time update cache data.
        """
        return self.__x_TU_cache, self.__sigma_TU_cache

    def __measurement_update(self, y_t):
        """Does measurement update step of the Kalman filter.

        :param y_t: Current altitude measurement.
        """
        # this is a 2x2 matrix
        the_inv = self.__C@self.__sigma_TU@self.__C.T + self.__R
        det_of_inv = the_inv[0, 0]*the_inv[1, 1] - the_inv[0, 1]*the_inv[1, 0]
        the_inv[0, 0], the_inv[1, 1] = the_inv[1, 1], the_inv[0, 0] 
        the_inv[0, 1] = -the_inv[0, 1] 
        the_inv[1, 0] = -the_inv[1, 0] 
        the_inv = the_inv/det_of_inv

        temp = self.__sigma_TU@self.__C.T@the_inv
        self.__x_MU = self.__x_TU + temp@(y_t - self.__C@self.__x_TU)
        self.__sigma_MU = self.__sigma_TU - temp@self.__C@self.__sigma_TU
        self.__cache_MU_values()
    
    def __time_update(self):
        """Does time update step of the kalman filter.
        """
        self.__x_TU = self.__At@self.__x_MU + self.__Bt@self.__ut
        self.__sigma_TU = self.__At@self.__sigma_MU@self.__At.T + self.__Bt@self.__N@self.__Bt.T + self.__Q.T
        self.__cache_TU_values()

    def reset(self):
        """reset the kalman filter velocity estimate.
        NOTE: only call this if the drone is close to ground and/ or the system dynamics are altered.
        """
        self.__x_MU[1, 0] = 0.

    def run(self, Tt, alpha_t, pitch_rad, roll_rad, y_t, heading=0.):
        """Runs the Kalman filter for one step

        :param Tt: Current normalized throttle reference.
        :param pitch_rad: Current drone pitch in radians.
        :param roll_rad: Current drone roll in radians.
        :param y_t: Current altitude measurement in meters.
        :return: State estimate.
        """
        # Check if altitude measurement is nan or outlier (which is indicated by -1/1000).
        self.__is_yt_not_nan = not (np.isnan(y_t[0, 0]) or y_t[0, 0] < 0 or y_t[0, 0] == None) and not (np.isnan(y_t[1, 0]) or y_t[1, 0] < 0 or y_t[1, 0] == None)
        # Update the throttle reference.
        self.__update_Tt(Tt)
        self.__update_alpha_t(alpha_t)
        self.__update_ut(pitch_rad, roll_rad, heading)
        # update the system matrix At.
        self.__update_Bt()
        # only do the measurement update if a valid measurement is received.
        if self.__is_yt_not_nan:
            self.__measurement_update(y_t) # Do the measurement update.
        self.__time_update() # Do the time update.
        # return measurement update estimate if a valid measurement is received else reuturn time update estimate.
        return self.__x_MU if self.__is_yt_not_nan else self.__x_TU
    

if __name__ == "__main__":
    kf = PositionKalmanFilter()
    x = 0
    v = 0
    for i in range(0, 20):
        # check if x and estimate[0, 0], v and estimate[2, 0] match.
        x = x + 0.1*v + 5e-5
        v = v + 1e-3
        print(kf.run(0.5, 20, 0.001, 0, np.array([[x], [1]])), x, v)
 
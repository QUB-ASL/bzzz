# TODO: Documentation
import numpy as np
import math

class KalmanFilter:
    def __init__(self, sampling_frequency=10, initial_Tt=0., x_tilde_0=np.zeros((4, 1)), P_0=np.eye(4, 4)*100, cache_values=False, overwrite_x_MU=None, overwrite_sigma_MU=None) -> None:
        self.__fs = sampling_frequency
        self.__Ts = 1/self.__fs
        self.__is_yt_not_nan = True

        # Normalized Throttle reference, range [0, 1]
        self.__Tt = initial_Tt
        # System dynamics
        self.__At = self.__update_At()
        self.__C = np.array([[1, 0, 0, 0]])

        # Process noise
        self.__Q = np.diagflat([1e-4, 1, 9.8, 1e-3])
        # Measurement noise
        self.__R = 0.1

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

    def __update_At(self):
        k_t = 0.5*self.__Ts**2

        self.__At = np.array([
            [1, self.__Ts, k_t*self.__Tt, k_t],
            [0, 1, self.__Ts*self.__Tt, self.__Ts],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

    def __update_Tt(self, Tt, pitch_rad, roll_rad):
        self.__Tt = math.cos(pitch_rad) * math.cos(roll_rad) * float(Tt)

    def MU_cache(self):
        return self.__x_MU_cache, self.__sigma_MU_cache
    
    def TU_cache(self):
        return self.__x_TU_cache, self.__sigma_TU_cache

    def __measurement_update(self, y_t):
        # this is just a number
        the_inv = self.__C@self.__sigma_TU@self.__C.T + self.__R
        the_inv = 1/the_inv
        temp = the_inv*self.__sigma_TU@self.__C.T
        self.__x_MU = self.__x_TU + temp@(y_t - self.__C@self.__x_TU)
        self.__sigma_MU = self.__sigma_TU - temp@self.__C@self.__sigma_TU
        self.__cache_MU_values()
    
    def __time_update(self):
        self.__x_TU = self.__At@self.__x_MU
        self.__sigma_TU = self.__At@self.__sigma_MU@self.__At.T + self.__Q
        self.__cache_TU_values()

    def reset(self, y_t, initial_Tt=0):
        self.__x_MU[1, 0] = 0.
        # x_tilde_0 = self.__x_MU if self.__is_yt_not_nan else self.__x_TU
        # reset the altitude estimate to current measurement and velocity estimate to zero
        # x_tilde_0[0, 0] = y_t
        # x_tilde_0[1, 0] = 0
        # p_0 = self.__sigma_MU if self.__is_yt_not_nan else self.__sigma_TU
        # self.__init__(sampling_frequency=self.__fs, initial_Tt=initial_Tt, x_tilde_0=x_tilde_0, P_0=p_0, cache_values=self.__cache_values, overwrite_x_MU=x_tilde_0, overwrite_sigma_MU=np.zeros((4, 4)))        

    def run(self, Tt, pitch_rad, roll_rad, y_t):
        self.__is_yt_not_nan = not (np.isnan(y_t) or y_t < 0)
        self.__update_Tt(Tt, pitch_rad, roll_rad)
        self.__update_At()
        if self.__is_yt_not_nan:
            self.__measurement_update(y_t)
        self.__time_update()
        return self.__x_MU if self.__is_yt_not_nan else self.__x_TU
 
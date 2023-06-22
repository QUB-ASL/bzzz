# TODO: Documentation
import numpy as np

class KalmanFilter:
    def __init__(self, sampling_frequency=10, initial_Tt=0., x_tilde_0=np.zeros((4, 1)), P_0=np.eye(4, 4)*100, cache_values=False) -> None:
        self.__fs = sampling_frequency
        self.__Ts = 1/self.__fs

        # Normalized Throttle reference, range [0, 1]
        self.__Tt = initial_Tt
        # System dynamics
        self.__At = self.__update_At()
        self.__C = np.array([[1, 0, 0, 0]])

        # Process noise
        self.__Q = np.eye(4, 4)*10**-5
        # Measurement noise
        self.__R = 10**-3

        # initial conditions
        self.__x_hat_0_minus1 = x_tilde_0
        self.__sigma_0_minus1 = P_0
        
        # Measurement update
        self.__x_MU = None
        self.__sigma_MU = None

        # Time update
        self.__x_TU = x_tilde_0
        self.__sigma_TU = P_0

        self.__cache_MU_values = lambda : ()
        self.__cache_TU_values = lambda : ()

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
        self.__At = np.array([
            [1, self.__Ts, 0, 0],
            [0, 1, self.__Ts*self.__Tt, self.__Ts],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

    def __update_Tt(self, Tt):
        self.__Tt = Tt

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

    def run(self, Tt, y_t):
        self.__update_Tt(Tt)
        self.__update_At()
        self.__measurement_update(y_t)
        self.__time_update()
        return self.__x_MU
 
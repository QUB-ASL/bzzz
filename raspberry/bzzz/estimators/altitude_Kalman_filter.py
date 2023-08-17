import numpy as np

class KalmanFilter:
    """This is a Kalman filter for estimating altitude hold related parameters.
    """
    def __init__(self, sampling_frequency=10, initial_Tt=0., x_tilde_0=np.zeros((4, 1)), P_0=np.eye(4, 4)*100, cache_values=False):
        """Constructor

        :param sampling_frequency: KF sampling frequency, defaults to 10
        :param initial_Tt: Initial throttle reference to the system, defaults to 0.
        :param x_tilde_0: Intial conditions; initial state guess for the KF, defaults to np.zeros((4, 1))
        :param P_0: Iniitial conditions: initial state guess variance, defaults to np.eye(4, 4)*100
        :param cache_values: Enables caching KF values if True, defaults to False
        """
        self.__fs = sampling_frequency
        self.__Ts = 1/self.__fs

        # Normalized Throttle reference, range [0, 1]
        self.__Tt = initial_Tt
        # System dynamics
        self.__At = self.__update_At()
        self.__C = np.array([[1, 0, 0, 0]])

        # Process noise
        self.__Q = np.eye(4, 4)*1e-5
        # Measurement noise
        self.__R = 1e-3

        # initial conditions
        self.__x_hat_0_minus1 = x_tilde_0
        self.__sigma_0_minus1 = P_0
        
        # Measurement update
        self.__x_MU = None
        self.__sigma_MU = None

        # Time update
        self.__x_TU = x_tilde_0
        self.__sigma_TU = P_0

        # Point to a function that does nothing if caching is not enabled.
        self.__cache_MU_values = lambda : ()
        self.__cache_TU_values = lambda : ()

        if cache_values:
            # Measurement update cache
            self.__x_MU_cache = []
            self.__sigma_MU_cache = []

            def cache_MU():
                self.__x_MU_cache.append(self.__x_MU)
                self.__sigma_MU_cache.append(self.__sigma_MU)

            # point to MU caching function
            self.__cache_MU_values = cache_MU

            # Time update cache
            self.__x_TU_cache = []
            self.__sigma_TU_cache = []

            def cache_TU():
                self.__x_TU_cache.append(self.__x_TU)
                self.__sigma_TU_cache.append(self.__sigma_TU)

            # point to TU caching function
            self.__cache_TU_values = cache_TU
            # cache first MU from above
            self.__cache_TU_values()

    def __update_At(self):
        """Update state matrix At. 
        NOTE: This function should be called whenever Tt is updated.
        """
        self.__At = np.array([
            [1, self.__Ts, 0, 0],
            [0, 1, self.__Ts*self.__Tt, self.__Ts],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

    def __update_Tt(self, Tt):
        """Update the throttle reference/ system input.

        :param Tt: Current normalized throttle reference.
        """
        self.__Tt = Tt

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

    def __measurement_update(self, y_t):
        """Does measurement update step of the Kalman filter.

        :param y_t: Current altitude measurement.
        """
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

    def update(self, Tt, y_t):
        """Runs the Kalman filter update for one step

        :param Tt: Current normalized throttle reference.
        :param y_t: Current altitude measurement in meters.
        :return: State estimate.
        """
        self.__update_Tt(Tt)
        self.__update_At()
        self.__measurement_update(y_t)
        self.__time_update()
        return self.__x_MU
 
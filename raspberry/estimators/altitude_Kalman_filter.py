import numpy as np
from matplotlib import pyplot as plt

class KalmanFilter:
    def __init__(self, sampling_frequency=10, x_tilde_0=np.array([[0,]*4]).T, P_0=np.array([[1, 1, 1, 1],]*4), cache_values=False) -> None:
        self.__fs = sampling_frequency
        self.__Ts = 1/self.__fs

        # Normalized Throttle reference, range [0, 1]
        self.__Tt = 0.
        # System dynamics
        self.__At = self.__update_At()
        self.__C = np.array([[1, 0, 0, 0]])

        # Process noise
        self.__Q = np.array([
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1]
        ])
        # Measurement noise
        self.__R = 1

        # initial conditions
        self.__x_hat_0_minus1 = x_tilde_0
        self.__sigma_0_minus1 = P_0
        
        # Measurement update
        self.__x_hat_t_t = None
        self.__sigma_t_t = None

        # Time update
        self.__x_hat_t_plus1_t = x_tilde_0
        self.__sigma_t_plus1_t = P_0

        self.__cache_MU_values = lambda : ()
        self.__cache_TU_values = lambda : ()

        if cache_values:
            # Measurement update cache
            self.__x_hat_t_t_cache = []
            self.__sigma_t_t_cache = []

            def cache_MU():
                self.__x_hat_t_t_cache.append(self.__x_hat_t_t)
                self.__sigma_t_t_cache.append(self.__sigma_t_t)

            self.__cache_MU_values = cache_MU

            # Time update cache
            self.__x_hat_t_plus1_t_cache = []
            self.__sigma_t_plus1_t_cache = []

            def cache_TU():
                self.__x_hat_t_plus1_t_cache.append(self.__x_hat_t_plus1_t)
                self.__sigma_t_plus1_t_cache.append(self.__sigma_t_plus1_t)

            self.__cache_TU_values = cache_TU


    def __update_At(self):
        self.__At = np.array([
            [1, self.__Ts, 0, 0],
            [0, 1, self.__Ts*self.__Tt, self.__Ts],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

    def __update_Tt(self, Tt):
        self.__Tt = Tt

    def __measurement_update(self, y_t):
        temp = self.__C@self.__sigma_t_plus1_t@self.__C.T + self.__R
        temp = 1/temp
        temp = temp*self.__sigma_t_plus1_t@self.__C.T
        self.__x_hat_t_t = self.__x_hat_t_plus1_t + temp@(y_t - self.__C@self.__x_hat_t_plus1_t)
        self.__sigma_t_t = self.__sigma_t_plus1_t - temp@self.__C@self.__sigma_t_plus1_t
        self.__cache_MU_values()
    
    def __time_update(self):
        self.__x_hat_t_plus1_t = self.__At@self.__x_hat_t_t
        self.__sigma_t_plus1_t = self.__At@self.__sigma_t_t@self.__At.T + self.__Q
        self.__cache_TU_values()

    def run(self, Tt, y_t):
        self.__update_Tt(Tt)
        self.__update_At()
        self.__measurement_update(y_t)
        self.__time_update()
        return self.__x_hat_t_t
    

if __name__ == "__main__":
    kf = KalmanFilter()
    Tt = np.sin(100) + np.random.normal(0, 0.1, 100)
    y_t = np.cos(100) + np.random.normal(0, 0.1, 100)
    x_hat_t = np.zeros([100, 4, 1])
    for i in range(100):
        x_hat_t[i, :, :] = kf.run(Tt[i], y_t[i])

    plt.plot(x_hat_t[:, 0, 0])
    plt.plot(y_t)
    plt.legend([r"$\hat{x}_t$", r"$y_t$"])
    plt.show()

import numpy as np

def _tilt_correction(x, pitch_rad, roll_rad):
        return np.cos(pitch_rad) * np.cos(roll_rad) * x

class AltitudeHoldKalmanFilter:

    def __init__(self,            
                 initial_state,
                 initial_sigma,
                 state_cov,
                 meas_cov,
                 sampling_time=0.1):
        self.__sampling_time = sampling_time
        self.__C = np.array([[1, 0, 0, 0, 1, 0]
                             [1, 0, 0, 0, 0, 1]
                             [1, 0, 0, 0, 0, 0]])        
        self.__Q = state_cov
        self.__R = meas_cov
        self.__x_pred = initial_state    
        self.__sigma_pred = initial_sigma
        self.__x_meas = initial_state
        self.__sigma_meas = initial_sigma
        pass

    
    def __matrix_a(self, tau):
        k_t = 0.5 * self.__sampling_time**2
        return np.array([
                [1, self.__sampling_time, 0, 0, 0, 0],
                [0, 1, self.__sampling_time * tau, self.__sampling_time, 0, 0],
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0 ,1]])
    
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
        y_t = _tilt_correction(y_t, pitch_rad, roll_rad)
        # this is just a number
        the_inv = self.__C @ self.__sigma_pred @ self.__C.T + self.__R
        the_inv = 1/the_inv
        temp = the_inv * self.__sigma_pred @ self.__C.T
        self.__x_meas = self.__x_pred + temp @ (y_t - self.__C@self.__x_pred)
        self.__sigma_meas = self.__sigma_pred - temp@self.__C@self.__sigma_pred
    
    def __time_update(self, tau):
        """Does time update step of the kalman filter.
        """
        A = self.__matrix_a(tau)        
        self.__x_pred = A @ self.__x_meas.reshape((6, 1))
        self.__sigma_pred = A @ self.__sigma_meas @ A.T + self.__Q
    
    def update(self, tau, pitch_rad, roll_rad, y_t):
         tau_corr = _tilt_correction(tau, pitch_rad, roll_rad)
         if not np.isnan(y_t):
              self.__measurement_update(y_t, pitch_rad, roll_rad)
         else: 
              self.__x_meas = self.__x_pred
              self.__sigma_meas = self.__sigma_pred
         self.__time_update(tau_corr)
    
    def x_measured(self):
         return self.__x_meas

    def sigma_measured(self):
         return self.__sigma_meas
    
    def tau_eq_estimate(self):
         alpha_1_est, alpha_0_est = self.__x_meas[2], self.__x_meas[3]
         tau_eq_est = -alpha_0_est/alpha_1_est
         return tau_eq_est
        
    
    
     
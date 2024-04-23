import numpy as np

def _tilt_correction(x, pitch_rad, roll_rad):
        """
        Calculates the correct alttitude given 
        pitch and roll angles in radians.

        :param x: Measured alttitude. 
        :param pitch_rad: pitch in radians.
        :param roll_rad: roll in radians.
        """
        return np.cos(pitch_rad) * np.cos(roll_rad) * x

class AltitudeHoldKalmanFilter:
    """
    Class to for the altitude hold Kalman Filter.
    """

    def __init__(self,            
                 initial_state,
                 initial_sigma,
                 state_cov,
                 meas_cov,
                 sampling_time=0.02):
        """
        Initalise the altitude hold kalman filter.

        :param initial_state: Initial state of the drone.
                              Altitude defualts to 0.5 m.
                              Velocity defualts to 0 m/s.
                              Alpha one defualts to 3.
                              Alpha zero defualts to -1.
        :param initial_sigma: 
        :param state_cov: covariance of the states.
                          Altitude defualts to 0.001.
                          Velocity defualts to 0.01.
                          Alpha one defualts to 8.0e-07.
                          Alpha zero defualts to 1.74e-07.                 
        :param meas_cov: Measurement/sensor covariance.
                         ToF sensor defualts to 0.0001
        :param sampling_time: sampling time; defalts to 0.02s.
        """
        self.__sampling_time = sampling_time
        self.__C = np.array([[1, 0, 0, 0]])        
        self.__Q = state_cov
        self.__R = meas_cov
        self.__x_pred = initial_state    
        self.__sigma_pred = initial_sigma
        self.__x_meas = initial_state
        self.__sigma_meas = initial_sigma
        pass

    
    def __matrix_a(self, tau):
        """
        :param tau: Throttle perecntage

        Returns the A matrix
        """
        k_t = 0.5 * self.__sampling_time**2
        return np.array([
                [1, self.__sampling_time, k_t * self.__sampling_time, k_t],
                [0, 1, self.__sampling_time * tau, self.__sampling_time],
                [0, 0, 1, 0],
                [0, 0, 0, 1]])
    
    def __measurement_update(self,
                             y_t,
                             pitch_rad=0.,
                             roll_rad=0.):
        """
        Does measurement update step of the Kalman filter.

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
        """
        Does time update step of the kalman filter.
        :param tau: Throttle perecntage
        """
        A = self.__matrix_a(tau)        
        self.__x_pred = A @ self.__x_meas.reshape((4, 1))
        self.__sigma_pred = A @ self.__sigma_meas @ A.T + self.__Q
    
    def update(self, tau, pitch_rad, roll_rad, y_t):
         """
         Kalman Filter update.

         :param tau: Throttle perecntage.
         :param y_t: Current altitude measurement.
         :param pitch_rad: current drone pitch in radians.
         :param roll_rad: current drone roll in radians.
         """
         y_t = _tilt_correction(y_t, pitch_rad, roll_rad)
         if not np.isnan(y_t):
              self.__measurement_update(y_t, pitch_rad, roll_rad)
         else: 
              self.__x_meas = self.__x_pred
              self.__sigma_meas = self.__sigma_pred
         self.__time_update(tau)
    
    def x_measured(self):
         """
         Returns the state measurments
         """
         return self.__x_meas

    def sigma_measured(self):
         """
         Returns the sigma measurments
         """
         return self.__sigma_meas
    
    def tau_eq_estimate(self):
         """
         returns the equilibrium/hovering throttle as a percentage.
         """
         alpha_1_est, alpha_0_est = self.__x_meas[2], self.__x_meas[3]
         tau_eq_est = -alpha_0_est/alpha_1_est
         return tau_eq_est
        
    
    
     
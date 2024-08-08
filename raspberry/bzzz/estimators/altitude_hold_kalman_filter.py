import numpy as np

def _tilt_correction(x, pitch_rad, roll_rad):
        """
        Calculates the correct altitude given 
        pitch and roll angles in radians.

        :param x: Measured altitude. 
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
                 gnss_var_rtk,
                 gnss_var_no_rtk,
                 tof_var_low_alt,
                 bar_var,
                 tof_var_change_alt,
                 sampling_time=0.02):
        """
        Initialise the altitude hold kalman filter.

        :param initial_state: Initial state of the drone.
                              Altitude defaults to 0.5 m.
                              Velocity defaults to 0 m/s.
                              Alpha one defaults to 3.
                              Alpha zero defaults to -1.
        :param initial_sigma: 
        :param state_cov: covariance of the states.
                          Altitude defaults to 0.001.
                          Velocity defaults to 0.01.
                          Alpha one defaults to 8.0e-07.
                          Alpha zero defaults to 1.74e-07.  
        :param sampling_time: sampling time; defaults to 0.02s.
        """
        self.__sampling_time = sampling_time
        self.__C = np.array([[1, 0, 0, 0, 0, 0],
                             [1, 0, 0, 0, 1, 0],
                             [1, 0, 0, 0, 0, 1]])
        self.__C_no_gnss = np.array([[1, 0, 0, 0, 1, 0],
                                     [1, 0, 0, 0, 0, 1]])      
        self.__Q = state_cov
        self.__gnss_var_rtk = gnss_var_rtk
        self.__gnss_var_no_rtk = gnss_var_no_rtk
        self.__tof_var_low_alt = tof_var_low_alt
        self.__bar_var = bar_var
        self.__tof_var_change_alt = tof_var_change_alt
        self.__x_pred = initial_state.reshape((6, 1)) 
        self.__sigma_pred = initial_sigma
        self.__x_meas = initial_state
        self.__sigma_meas = initial_sigma
        self.__last_y_gnss = 0
        pass
    
    def __matrix_r(self,
                   y_t_tof,
                   rtk_status):
        """
        :param 

        Returns the A matrix
        """
        if rtk_status is True:
             gnss_var = self.__gnss_var_rtk
        else:
             gnss_var = self.__gnss_var_no_rtk
        
        if y_t_tof <= self.__tof_var_change_alt:
             tof_var = self.__tof_var_low_alt
        else:
             tof_var = np.square(0.0015*y_t_tof)

        return np.array([
                [gnss_var, 0, 0],
                [0, tof_var, 0],
                [0, 0, self.__bar_var]])
    
    def __matrix_a(self, tau):
        """
        :param tau: Throttle percentage

        Returns the A matrix
        """
        return np.array([
                [1, self.__sampling_time, 0, 0, 0, 0],
                [0, 1, self.__sampling_time, self.__sampling_time * tau, 0, 0],
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0 ,1]])
    
    def __measurement_update_all_sensors(self,
                                         y_t,
                                         rtk_status,
                                         pitch_rad=0.,
                                         roll_rad=0.):
        """
        Does measurement update step of the Kalman filter.

        :param y_t: Current altitude measurement.
        :param pitch_rad: current drone pitch in radians, defaults to 0.
        :param roll_rad: current drone roll in radians, defaults to 0.
        """
        R = self.__matrix_r(y_t[1], rtk_status)
        e = y_t.reshape((3, 1)) - self.__C @ self.__x_pred
        R_tilde = self.__C @ self.__sigma_pred @ self.__C.T + R
        self.__x_meas = self.__x_pred + ((self.__sigma_pred @ self.__C.T) 
                                         @ np.linalg.solve(R_tilde, e))
        self.__sigma_meas = self.__sigma_pred - (
                    (self.__sigma_pred @ self.__C.T) 
                    @ np.linalg.solve(R_tilde, self.__C @ self.__sigma_pred))
    
    def __measurement_update_no_gnss(self,
                                     y_t,
                                     rtk_status,
                                     pitch_rad=0.,
                                     roll_rad=0.):
        """Does measurement update step of the Kalman filter.
 
        :param y_t: Current altitude measurement.
        :param pitch_rad: current drone pitch in radians, defaults to 0.
        :param roll_rad: current drone roll in radians, defaults to 0.
        """
        y_t = y_t[1:3]
        R = self.__matrix_r(y_t[0], rtk_status)
        e = y_t.reshape((2, 1))  - self.__C_no_gnss @ self.__x_pred
        R_tilde = self.__C_no_gnss @ self.__sigma_pred @ self.__C_no_gnss.T 
        + R[1:3,1:3]
        self.__x_meas = self.__x_pred + (
                              (self.__sigma_pred @ self.__C_no_gnss.T) 
                              @ np.linalg.solve(R_tilde, e))
        self.__sigma_meas = self.__sigma_pred - (
             (self.__sigma_pred @ self.__C_no_gnss.T) 
             @ np.linalg.solve(R_tilde, self.__C_no_gnss @ self.__sigma_pred))
    
    def __time_update(self, tau):
        """
        Does time update step of the kalman filter.
        :param tau: Throttle percentage
        """
        A = self.__matrix_a(tau)        
        self.__x_pred = A @ self.__x_meas.reshape((6, 1))
        self.__sigma_pred = A @ self.__sigma_meas @ A.T + self.__Q
    
    def update(self, tau, pitch_rad, roll_rad, y_t, rtk_status):
         """
         Kalman Filter update.

         :param tau: Throttle percentage.
         :param y_t: Current altitude measurement.
         :param pitch_rad: current drone pitch in radians.
         :param roll_rad: current drone roll in radians.
         """
         y_t[0] = _tilt_correction(y_t[0], pitch_rad, roll_rad)
         y_t[1] = _tilt_correction(y_t[1], pitch_rad, roll_rad)
         y_t[2] = _tilt_correction(y_t[2], pitch_rad, roll_rad)
         if not np.isnan(y_t[1]):
             if self.__last_y_gnss == y_t[0]:
                 self.__measurement_update_no_gnss(y_t, 
                                                   rtk_status, 
                                                   pitch_rad, 
                                                   roll_rad)
             else:
                 self.__measurement_update_all_sensors(y_t, 
                                                       rtk_status, 
                                                       pitch_rad, 
                                                       roll_rad)
         else: 
              self.__x_meas = self.__x_pred
              self.__sigma_meas = self.__sigma_pred
         self.__time_update(tau)
         self.__last_y_gnss = y_t[0]
    
    def x_measured(self):
         """
         Returns the state measurements
         """
         return self.__x_meas

    def sigma_measured(self):
         """
         Returns the sigma measurements
         """
         return self.__sigma_meas
    
    def tau_eq_estimate(self):
         """
         returns the equilibrium/hovering throttle as a percentage.
         """
         alpha_0_est, alpha_1_est = self.__x_meas[2], self.__x_meas[3]
         tau_eq_est = -alpha_0_est/alpha_1_est
         return tau_eq_est
class AltitudeController:
    """
    Class to control the altitude of the quadcopter.
    """

    def __init__(self):
        """
        Initalise the altitude controller.
        """
        self.__altitude_reference = 1
        self.__p_gain = 0.5
        self.__d_gain = 0.16
        self.__tau_eq = 0.4

    def increment_reference(self, by=0):
        """
        Increment the altitude reference in meters.
        """
        self.__altitude_reference += by
    
    def control_action(self, z_est, vz_est):
        """
        calculates the throttle percentage required
        to keep the quadcopter at constant altitude.
        """
        altitude_error = z_est - self.__altitude_reference
        u = self.__tau_eq + self.__p_gain * altitude_error + self.__d_gain * vz_est
        return u 

    def set_p_gain(self, p_gain):
        """
        Sets the P gain for the altitude hold controller.
        This gain is multiplied with the altitude error. 
        """
        self.__p_gain = p_gain

    def set_d_gain(self, d_gain):
        """
        Sets the D gain for the altitude hold controller.
        This gain is multiplied with the velocity estmiate. 
        """
        self.__d_gain = d_gain
    
    def set_altitude_reference(self, altitude_reference):
        """
        sets the altitude reference height in meters from the ground.
        """
        self.__altitude_reference = altitude_reference
    
    def set_tau_eq(self, tau_eq):
        """
        Sets the equilibrium/hovering throttle as a percentage.
        """
        self.__tau_eq = tau_eq

    def altitude_reference(self):
        """
        Returns the altitude reference height in meters from the ground.
        """
        return self.__altitude_reference


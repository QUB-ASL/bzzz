class AltitudeController:

    def __init__(self):
        self.__altitude_reference = 1
        self.__p_gain = 5
        self.__d_gain = 3
        self.__tau_eq = 0.4

    def increment_reference(self, by=0):
        self.__altitude_reference += by
    
    def control_action(self, z_est, vz_est):
        altitude_error = z_est - self.__altitude_reference
        u = self.__tau_eq + self.__p_gain * altitude_error + self.__d_gain * vz_est
        return u 

    def set_p_gain(self, p_gain):
        self.__p_gain = p_gain

    def set_d_gain(self, d_gain):
        self.__d_gain = d_gain
    
    def set_altitude_reference(self, altitude_reference):
        self.__altitude_reference = altitude_reference
    
    def set_tau_eq(self, tau_eq):
        self.__tau_eq = tau_eq

    def altitude_reference(self):
        return self.__altitude_reference


from scipy.interpolate import CubicSpline


class BLDC:
    def __init__(self) -> None:
        self.__max_torque = None
        self.__max_RPM = None
        self.__KV_rating = None
        
        self.__VRMS_vs_RPM_no_load_profile = None
        self.__VRMS_vs_RPM_no_load_spline = CubicSpline(*self.__VRMS_vs_RPM_no_load_profile)

        self.__RPM_vs_torque_profile = None
        self.__RPM_vs_torque_spline = CubicSpline(*self.__RPM_vs_torque_profile)
        self.__torque_vs_iRMS_profile = None
        self.__torque_vs_iRMS_spline = CubicSpline(*self.__torque_vs_iRMS_profile)
        self.__efficiency_vs_torque_profile = None
        self.__efficiency_vs_torque_spline = CubicSpline(*self.__efficiency_vs_torque_profile)

        self.__mass = None
        self.__moment_of_inertia = None

    def __VRMS_to_RPM(self, VRMS):
        return self.__VRMS_vs_RPM_no_load_spline(VRMS)
    
    def __RPM_to_torque(self, RPM):
        return self.__RPM_vs_torque_spline(RPM)
    
    def __torque_to_iRMS(self, torque):
        return self.__torque_vs_iRMS_spline(torque)
    
    def simulate(self, VRMS):
        RPM = self.__VRMS_to_RPM(VRMS)
        torque_Nm = self.__RPM_to_torque(RPM)
        iRMS_amp = self.__torque_to_iRMS(torque_Nm)
        return RPM, torque_Nm, iRMS_amp
from scipy.interpolate import CubicSpline

class ESC:
    def __init__(self) -> None:
        self.__amperage = None

        self.__percentile_PWM_vs_chopping_frequency_profile = None
        self.__percentile_PWM_vs_duty_cycle_profile = None
        self.__percentile_PWM_vs_percentile_VRMS_profile = None
        
        self.__percentile_PWM_vs_chopping_frequency_spline = CubicSpline(*self.__percentile_PWM_vs_chopping_frequency_profile)
        self.__percentile_PWM_vs_duty_cycle_spline = CubicSpline(*self.__percentile_PWM_vs_duty_cycle_profile)
        self.__percentile_PWM_vs_percentile_VRMS_spline = CubicSpline(*self.__percentile_PWM_vs_percentile_VRMS_profile)

        self.__mass_kg = None
        self.__moment_of_inertia_kg_msq = None

    def __percentile_PWM_to_chopping_frequency(self, PWM_percentile):
        return self.__percentile_PWM_vs_chopping_frequency_spline(PWM_percentile)
    
    def __percentile_PWM_to_duty_cycle(self, PWM_percentile):
        return self.__percentile_PWM_vs_duty_cycle_spline(PWM_percentile)
        
    def __percentile_PWM_to_percentile_VRMS(self, PWM_percentile):
        return self.__percentile_PWM_vs_percentile_VRMS_spline(PWM_percentile)
    
    def is_current_overload(self, current_demand_amp):
        return current_demand_amp > self.__amperage
    
    def max_amperage(self):
        return self.__amperage
    
    def simulate(self, PWM_percentile):
        VRMS_percentile = self.__percentile_PWM_to_percentile_VRMS(PWM_percentile)
        return VRMS_percentile
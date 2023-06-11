from scipy.interpolate import CubicSpline

class Battery:
    def __init__(self) -> None:
        self.__capacity_mAh = None
        self.__max_output_current_amp = None

        self.__num_cells = None
        self.__voltage_per_cell = None

        self.__current_EMF = self.__num_cells*self.__voltage_per_cell
        
        self.__internal_resistance_ohm = None
        self.__discharge_profile_per_cell = None  # this is capacity (x) vs EMF (y)
        self.__discharge_profile_per_cell_spline = CubicSpline(*self.__discharge_profile_per_cell)

        self.__mass_kg = None
        self.__moment_of_inertia_kg_msq = None
    
    def __current_capacity(self):
        return self.__capacity_mAh
    
    def __update_capacity(self, current_drawn_amp, for_period_sec):
        self.__capacity_mAh -= current_drawn_amp*for_period_sec*100

    def __update_current_EMF(self):
        self.__current_EMF = self.__discharge_profile_per_cell_spline(self.__current_capacity())
    
    def __current_output_voltage(self, current_drawn_amp):
        return self.__current_EMF - current_drawn_amp*self.__internal_resistance_ohm
    
    def current_EMF(self):
        return self.__current_EMF

    def is_current_overload(self, current_drawn_amp):
        return current_drawn_amp > self.__max_output_current_amp
    
    def simulate(self, current_drawn_amp, for_period_sec):
        if current_drawn_amp <= self.__max_output_current_amp:
            self.__update_capacity(current_drawn_amp, for_period_sec)
            self.__update_current_EMF()
            current_output_voltage = self.__current_output_voltage(current_drawn_amp)
            return current_output_voltage, self.__capacity_mAh


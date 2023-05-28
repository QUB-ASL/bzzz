# TODO: implement proper code for a particular sensor
# TODO: add proper Doc strings
# NOTE: for now, we are just passing dummy values

from filters import median_filter

class PressureSensor:
    def __init__(self, num_latest_readings_to_keep: int = 5):
        self._current_pressure = None
        self._previous_pressure = None
        self._pressure_readings_list = None
        self._pressure_readings_list_current_index = None
        self._num_latest_readings_to_keep = num_latest_readings_to_keep
        
        self._current_altitude = None
        self._previous_altitude = None

        self._init_pressure_sensor()

    def _init_pressure_sensor(self):
        self._pressure_readings_list = list()
        self._pressure_readings_list_current_index = 0
        # TODO: add code to init pressure sensor
        for i in range(self._num_latest_readings_to_keep):
            self._pressure_readings_list.append(self._get_current_pressure_measurement())
        self.update_altitude()

    @property
    def pressure(self):
        return self._current_pressure
    
    @pressure.setter
    def pressure(self, val):
        self._current_pressure = val

    @property
    def altitude(self):
        self.update_altitude()
        return self._current_altitude
    
    @altitude.setter
    def altitude(self, val):
        self._current_altitude = val

    def _get_current_pressure_measurement(self):
        # TODO: add code to get measurement from sensor
        pressure_reading = 20  # dummy reading
        return pressure_reading

    def _update_pressure(self):
        pressure_reading = self._get_current_pressure_measurement()  # dummy value for now, actually should have a proper value
        self._previous_pressure = self._current_pressure
        self._pressure_readings_list[self._pressure_readings_list_current_index] = pressure_reading
        if 0 <= self._pressure_readings_list_current_index < self._num_latest_readings_to_keep - 1:
            self._pressure_readings_list_current_index += 1
        else:
            self._pressure_readings_list_current_index = 0
        self._current_pressure = median_filter(self._pressure_readings_list, self._num_latest_readings_to_keep)

    def _calculate_altitude_from_pressure(self):
        # TODO: add code to calculate altitude from pressure
        self._current_altitude = self._current_pressure

    def update_altitude(self):
        self._update_pressure()
        self._calculate_altitude_from_pressure()       
    
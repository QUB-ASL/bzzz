# TODO: implement proper code for a particular sensor
# TODO: add proper Doc strings
# NOTE: for now, we are just passing dummy values

from filters import median_filter

class TimeOfFlightSensor:
    def __init__(self, num_latest_readings_to_keep: int = 5):
        self._current_travel_time = None
        self._travel_time_readings_list = None
        self._travel_time_readings_list_current_index = None
        self._num_latest_readings_to_keep = num_latest_readings_to_keep
        
        self._current_altitude = None
        self._previous_altitude = None

        self._init_ToF_sensor()

    def _init_ToF_sensor(self):
        self._travel_time_readings_list = list()
        self._travel_time_readings_list_current_index = 0
        # TODO: add code to init pressure sensor
        for i in range(self._num_latest_readings_to_keep):
            self._travel_time_readings_list.append(self._get_current_ToF_measurement())
        self.update_altitude()

    @property
    def altitude(self):
        self.update_altitude()
        return self._current_altitude
    
    @altitude.setter
    def altitude(self, val):
        self._current_altitude = val

    def _get_current_ToF_measurement(self):
        # TODO: add code to get measurement from sensor
        ToF_reading = 20  # dummy reading
        return ToF_reading

    def _update_ToF(self):
        ToF_reading = self._get_current_ToF_measurement()  # dummy value for now, actually should have a proper value
        self._travel_time_readings_list[self._travel_time_readings_list_current_index] = ToF_reading
        if 0 <= self._travel_time_readings_list_current_index < self._num_latest_readings_to_keep - 1:
            self._travel_time_readings_list_current_index += 1
        else:
            self._travel_time_readings_list_current_index = 0
        self._current_travel_time = median_filter(self._travel_time_readings_list, self._num_latest_readings_to_keep)

    def _calculate_altitude_from_ToF(self):
        # TODO: add code to calculate altitude from time of flight
        self._current_altitude = self._current_travel_time

    def update_altitude(self):
        self._update_ToF()
        self._calculate_altitude_from_ToF()       
    
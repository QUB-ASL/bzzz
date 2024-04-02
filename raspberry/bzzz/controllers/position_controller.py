from raspberry.bzzz.sensors.gnss import Gnss
from raspberry.bzzz.read_sbus.radioData import RadioData

# Position Controller Class
class PositionController:

    def __init__(self):
        self.__gnss_device = None
        self.__radio_data = None
        self.__target_lat = None
        self.__target_lon = None
        self.__kp = 1.0
        self.__ki = 0.01
        self.__kd = 0.5
        self.__previous_error_lat = 0.0
        self.__integral_lat = 0.0
        self.__previous_error_lon = 0.0
        self.__integral_lon = 0.0

    def set_gnss_device(self, gnss_device):
        self.__gnss_device = gnss_device
    
    def set_radio_data(self, radio_data):
        self.__radio_data = radio_data

    def set_reference_position(self):
        gps_data = self.__gnss_device.all_gnss_data
        self.__target_lat, self.__target_lon, _ = gps_data

    def control_action(self):
        if self.__target_lat is None or self.__target_lon is None:
            return None, None

        gps_data = self.__gnss_device.all_gnss_data
        current_lat, current_lon, _ = gps_data
        
        # Calculate PID components for latitude
        error_lat = self.__target_lat - current_lat
        self.__integral_lat += error_lat
        derivative_lat = error_lat - self.__previous_error_lat

        # Calculate PID output for latitude
        lat_control_signal = (self.__kp * error_lat) + (self.__ki * self.__integral_lat) + (self.__kd * derivative_lat)
        self.__previous_error_lat = error_lat

        # Calculate PID components for longitude
        error_lon = self.__target_lon - current_lon
        self.__integral_lon += error_lon
        derivative_lon = error_lon - self.__previous_error_lon

        # Calculate PID output for longitude
        lon_control_signal = (self.__kp * error_lon) + (self.__ki * self.__integral_lon) + (self.__kd * derivative_lon)
        self.__previous_error_lon = error_lon

        return lat_control_signal, lon_control_signal

    def apply_control(self):
        lat_control_signal, lon_control_signal = self.control_action()
        if lat_control_signal is not None and lon_control_signal is not None:
            self.__apply_lat_control(lat_control_signal)
            self.__apply_lon_control(lon_control_signal)
    
    def __apply_lat_control(self, control_signal):
        self.__radio_data.set_roll(control_signal)

    def __apply_lon_control(self, control_signal):
        self.__radio_data.set_pitch(control_signal)

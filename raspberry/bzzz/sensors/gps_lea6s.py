import serial
import time
from threading import Thread, Lock


class Gpgll:
    """
    Geographic position data (latitude, longitude and UTC)
    """

    def __init__(self,
                 latitude,
                 longitude,
                 utc):
        self.__latitude = latitude  # latitude in degrees (N is positive)
        self.__longitude = longitude
        self.__utc = utc

    @property
    def latitude(self):
        """Latitude in degrees"""
        return self.__latitude

    @property
    def longitude(self):
        """Longitude in degrees"""
        return self.__longitude

    @property
    def utc(self):
        """UTC time status of position"""
        return self.__utc


class Gpgsv:
    """GPS satellites in view"""

    def __init__(self):
        pass


class GpsData:
    """GPS Data"""

    def __init__(self, gpgll, gpgsv):
        self.__gpgll = gpgll  # Geographic position
        self.__gpgsv = gpgsv  # GPS satellites in view

    @property
    def gpgll(self):
        return self.__gpgll

    @property.setter
    def gpgll(self, value):
        self.__gpgll = value

    @property
    def gpgsv(self):
        return self.__gpgsv

    @property.setter
    def gpgsv(self, value):
        self.__gpgsv = value


class GpsLea6SReader:

    def __init__(self,
                 serial_path="/dev/tty.usbmodem14301",
                 baud=500000):
        # Initialise objects to store various measurements
        self.__gps_data = GpsData()

        self.__thread = Thread(target=self.__get_measurements_in_background_t,
                               args=[serial_path, baud])
        self.__thread.start()

    def __get_measurements_in_background_t(self, serial_path, baud):
        ser = serial.Serial(serial_path, baud, timeout=1)
        ser.reset_input_buffer()
        while True:
            if ser.in_waiting > 0:
                sensor_data = ser.readline().decode('utf-8').strip()
                tokens = sensor_data.split(",")
                msg_key = tokens[0]
                # TODO Parse the various data
                if msg_key == "$GPGLL":
                    # TODO implement method __parse_gpgll(tokens)
                    # TODO tokens[1] and tokens[3] could be Null!
                    latitude = float(tokens[1])/100
                    longitude = float(tokens[3])/100
                    # TODO read and store UTC time
                    # NOTE See how this is implemented in `anemometer` and adapt
                    #      the code we have there
                elif msg_key == "$GPGSV":
                    # TODO implement method __parse_gpgsv(tokens)
                    pass

    @property
    def gps_data(self):
        """
        GPS data object
        """
        return self.__gps_data


my_sensor = GpsLea6SReader()
print("Thread is running in background")
time.sleep(2)

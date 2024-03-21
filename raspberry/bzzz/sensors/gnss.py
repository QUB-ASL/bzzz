import serial
import numpy as np
from threading import Thread, Lock
import time
import datetime
from .data_logger import DataLogger
from .filters import MedianFilter

def _deg_min_sec_to_decimal(degrees, minutes, direction):
    """
    Convert degrees-minutes-seconds from GNGLL to decimal
    :param degrees: degrees
    :param minutes: minutes
    :param direction: direction (can be one of 'N', 'W', 'E', 'S')
    :return: decimal representation of GPS coordinates
    """
    decimal_degrees = degrees + minutes / 60
    if direction in ['S', 'W']:  # need to be denoted with a negative value
        decimal_degrees *= -1
    return decimal_degrees

class Gnss:
    """
    GNSS Module

    This class is used to interface the GNSS Module
    """
    def __init__(self, 
                 serial_path="/dev/ttyACM0", 
                 baud=57600, 
                 window_length=3,
                 data_processor=MedianFilter(),
                 log_file=None,
                 max_samples=100000):
        """
        Initialises the GPS data handler with the default serial path and baud
        rate, sets up storage for latitude, longitude, and altitude, and starts
        a background thread to continuously read and parse GPS data.

        :param serial_path: Path to the serial port where the GPS is connected;
                            default: "/dev/ttyACM0"
        :param baud: baud rate of serial communication; defaults to 57600
        :param window_length: length of window of measurements; default: 3
        :param data_processor: data processor on buffer of measurements; 
                               default: MedianFilter()
        :param log_file: file name to log data; default: None 
        :param max_samples: maximum number of samples to record; 
                            default: 100000

        If `log_file` is None, the data is not logged; otherwise, on exit, 
        the data are stored in a CSV file

        Note: We assume that we receive 3 measurements from the anemometer
        """
        self.__lock = Lock()
        self.__thread = Thread(target=self.__get_measurements_in_background_t,
                               args=[serial_path, baud])
        self.__keep_going = True
        self.__window_length = window_length
        self.__values_cache = np.tile(np.nan, (self.__window_length, 3))
        self.__cursor = 0
        self.__data_processor = data_processor
        self.__log_file = log_file
        self.__max_samples = max_samples
        self.__calibrated = False  # Initialization of the __calibrated attribute
        self.__altitude_initilisation = np.nan
        if log_file is not None:
            feature_names = ("Date_Time", "Latitude", "Longitude", "Altitude")
            self.__logger = DataLogger(num_features=3,
                                       max_samples=max_samples,
                                       feature_names=feature_names)    
        self.__thread.start()
    
    def __get_measurements_in_background_t(self, serial_path, baud):
        """
        Continuously reads GPS data from the serial port, parsing GNGLL
        messages for latitude and longitude, and GPGSV messages for altitude,
        updating the object's GPS attributes accordingly. 

        :param serial_path: Serial port path
        :param baud: Baud rate for the serial connection
        """
        ser = serial.Serial(serial_path, baud, timeout=1)
        ser.reset_input_buffer()

        # Initialize default values for latitude, longitude, and altitude
        latitude = np.nan
        longitude = np.nan
        altitude = np.nan

        while self.__keep_going:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', 'ignore').strip()
                tokens = line.split(",")
                msg_key = tokens[0]

                if msg_key == "$GNGLL" and tokens[1] and tokens[3]:
                    lat_deg = int(float(tokens[1]) / 100)
                    lat_min = float(tokens[1]) % 100
                    latitude = _deg_min_sec_to_decimal(lat_deg, lat_min, 
                                                      tokens[2])

                    lon_deg = int(float(tokens[3]) / 100)
                    lon_min = float(tokens[3]) % 100
                    longitude = _deg_min_sec_to_decimal(lon_deg, lon_min, 
                                                       tokens[4])
                    
                elif msg_key == "$GNGGA" and len(tokens) > 5:
                    altitude = float(tokens[9])

                # Check if any of the values are NaN before saving or
                # processing
                if (not np.isnan(latitude) and not np.isnan(longitude) 
                        and not np.isnan(altitude)):
                    gnss_to_save = np.array([latitude, longitude, 
                                              altitude])    
                
                    with self.__lock:
                        self.__values_cache[self.__cursor, :] = gnss_to_save
                        if (self.__log_file is not None 
                                and self.__cursor < self.__max_samples):
                            data_to_log = self.__data_processor.process(
                                self.__values_cache[:, :], 
                                cursor=self.__cursor)
                            # Process the data only if it doesn't contain NaN
                            # values
                            if not np.isnan(data_to_log).any():
                                    current_timestamp = datetime.datetime.now()
                                    self.__logger.record(current_timestamp, 
                                                         data_to_log)
                        self.__cursor = ((self.__cursor + 1) 
                        % self.__window_length)

        ser.close()
        return

    def gnss_altitude_initilisation(self, num_samples=10):
        sum_altitudes = 0    
        """
        Returns the calibrated GNSS altitude based on the average 
        altitude measured in the first minute of readings.
        """
        i = 0
        while True:            
            current_altitude = self.altitude
            if not np.isnan(current_altitude):
                i += 1
                sum_altitudes += current_altitude
            if i == num_samples:
                break
        average_altitude = sum_altitudes / num_samples
        
        return average_altitude

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.__keep_going = False
        self.__thread.join()  # Wait for the thread to finish
        if self.__log_file is not None:
            self.__logger.save_to_csv(self.__log_file)

    @property
    def all_gnss_data(self):
        """
        Returns all GNSS data 

        This method returns all sensor data after the application of the data
        preprocessor specified in the constructor. The data is returned as a
        numpy array with the following data (in this order):
          - Latitude in decimal 
          - Longitude in decimal 
          - Altitude
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, :], 
                                                 cursor=self.__cursor)

    @property
    def latitude(self):
        """
        Returns Latitude position in decimal
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 0], 
                                                 cursor=self.__cursor)

    @property
    def longitude(self):
        """
        Returns Longitude position in decimal
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 1], 
                                                 cursor=self.__cursor)

    @property
    def altitude(self):
        """
        Returns the Altitude position
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 2], 
                                                 cursor=self.__cursor)
        
if __name__ == '__main__':

    while True:
        filename = datetime.datetime.now().strftime("Gnss_%d-%m-%y--%H-%M.csv")
        processor = MedianFilter()
        with Gnss(window_length=5,
                  data_processor=processor,
                  log_file=filename) as gnss_sensor:
            gnss_sensor.gnss_altitude_initilisation()
            time.sleep(600) # set time for how long you want to record data 
                            # for in seconds                
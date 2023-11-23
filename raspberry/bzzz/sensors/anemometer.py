import serial
import numpy as np
from threading import Thread, Lock
import abc
import time
import datetime
import csv


class DataProcessor(abc.ABC):
    """Abstract data processor"""

    def __init__(self):
        pass

    @abc.abstractmethod
    def process(self, data, cursor=0):
        """
        Data processing method (abstract; no implementation)

        :param data: numpy array of data  
        :param cursor: index of the *current* measurement 
        """
        pass


class AverageFilter(DataProcessor):
    """Moving average filter"""

    def __init__(self):
        super().__init__()

    def process(self, data, cursor=0):
        return np.nanmean(data, axis=0)


class MedianFilter(DataProcessor):
    """
    Median filter

    The median filter is recommended to be used when the window size is odd.
    """

    def __init__(self):
        super().__init__()

    def process(self, data, cursor=0):
        return np.nanmedian(data, axis=0)


class NoFilter(DataProcessor):
    """No filter: the latest data point is returned"""

    def __init__(self):
        super().__init__()

    def process(self, data, cursor):
        return data[cursor]


class DataLogger:
    """A data logger to be used with a sensor"""

    def __init__(self, num_features, max_samples=10000, feature_names=None):
        """
        Construct a new instance of DataLogger

        :param num_features: number of features
        :param max_samples: buffer size (maximum number of samples); default: 10000
        :param feature_names: list of feature names (str)
        """
        self.__data_vault = np.zeros(
            (max_samples, num_features), dtype=np.float64)
        self.__timestamps_vault = np.array(
            [datetime.datetime.now()] * max_samples)
        self.__feature_names = feature_names
        self.__cursor = 0

    def record(self, timespamp, datum):
        """
        Record/log data in memory

        :param timestamp: timestamp of measurement(s)
        :param datum: measurement (float or numpy array)
        """
        self.__data_vault[self.__cursor, :] = datum
        self.__timestamps_vault[self.__cursor:] = timespamp
        self.__cursor = self.__cursor + 1

    def save_to_csv(self, filename):
        """
        Save the data to a CSV file

        :param filename: file name (relative or absolute path)
        """
        with open(filename, "w") as fh:
            writer = csv.writer(fh)
            writer.writerow(self.__feature_names)
        with open(filename, "a+") as fh:
            writer = csv.writer(fh)
            data_to_record = np.hstack((np.reshape(self.__timestamps_vault[:self.__cursor], (
                self.__cursor, 1)), self.__data_vault[:self.__cursor, :]))
            writer.writerows(data_to_record)


class Anemometer:
    """
    Anemometer sensor

    This class is used to interface the anemometer
    """

    def __init__(self,
                 serial_path='/dev/ttyS0',
                 baud=115200,
                 window_length=3,
                 data_processor=MedianFilter(),
                 log_file=None,
                 max_samples=100000):
        """
        Create a new instance of Anemometer

        :param serial_path: serial path; defaults to /dev/ttyS0 on RPi
        :param baud: baud rate of serial communication; defaults to 115200
        :param window_length: length of window of measurements; default: 3
        :param data_processor: data processor on buffer of measurements; default: MedianFilter()
        :param log_file: file name to log data; default: None 
        :param max_samples: maximum number of samples to record; default: 100000

        If `log_file` is None, the data is not logged; otherwise, on exit, 
        the data are stored in a CSV file

        Note: We assume that we receive 7 measurements from the anemometer
        """
        # A lock is used to guarantee that we won't be reading the data
        # while the thread in the background is writing it
        self.__lock = Lock()
        self.__thread = Thread(target=self.__get_measurements_in_background_t,
                               args=[serial_path, baud])
        self.__keep_going = True
        self.__window_length = window_length
        self.__values_cache = np.tile(np.nan, (self.__window_length, 7))
        self.__cursor = 0
        self.__data_processor = data_processor
        self.__log_file = log_file
        self.__max_samples = max_samples
        if log_file is not None:
            feature_names = ("Date_Time", "Wind_Speed", "Wind_Speed_2D",
                             "H_direction", "V_direction", "U_axis",
                             "V_axis", "W_axis")
            self.__logger = DataLogger(num_features=7,
                                       max_samples=max_samples,
                                       feature_names=feature_names)
        self.__thread.start()

    def __get_measurements_in_background_t(self, serial_path, baud):
        """
        This is a thread that runs in the background to connect to the 
        serial and collect measurements, which are stored in a buffer

        :param serial_path: serial path
        :param baud: baud rate of serial communication
        """
        ser = serial.Serial(serial_path, baud, timeout=1)
        ser.reset_input_buffer()
        while True:
            if ser.in_waiting > 0:
                sensor_data = ser.readline().decode('utf-8').strip()
                split_data = sensor_data.split()
                split_data_float = np.array(
                    [float(x) for x in split_data],
                    dtype=np.float64)
                with self.__lock:
                    self.__values_cache[self.__cursor, :] = split_data_float
                    # If the caller wants to log (log_file specified) there is still space
                    # in the log file, record data
                    if self.__log_file is not None and self.__cursor < self.__max_samples:
                        data_to_log = self.__data_processor.process(
                            self.__values_cache[:, :], cursor=self.__cursor)
                        current_timestamp = datetime.datetime.now()
                        self.__logger.record(current_timestamp, data_to_log)
                    self.__cursor = (self.__cursor + 1) % self.__window_length
                if not self.__keep_going:
                    ser.close()
                    return

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.__keep_going = False
        time.sleep(0.05)
        if self.__log_file is not None:
            self.__logger.save_to_csv(self.__log_file)

    @property
    def all_sensor_data(self):
        """
        Returns all sensor data 

        This method returns all sensor data after the application of the data 
        preprocessor specified in the construtor. The data is returned as a numpy 
        array with the following data (in this order):
          - magnitude of wind speed in m/s
          - magnitude of 2D wind speed in m/s
          - horizontal direction in degrees
          - vertical direction in degrees
          - wind speed along u-axis in m/s
          - wind speed along v-axis in m/s
          - wind speed along w-axis in m/s
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, :], cursor=self.__cursor)

    @property
    def wind_speed_3d(self):
        """
        Returns the 3D wind speed magnitude in m/s (processed)
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 0], cursor=self.__cursor)

    @property
    def wind_speed_2d(self):
        """
        Returns the 2D wind speed magnitude in m/s (processed)
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 1], cursor=self.__cursor)

    @property
    def horizontal_wind_direction(self):
        """
        Returns the horizontal wind direction in degrees (processed)
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 2], cursor=self.__cursor)

    @property
    def vertical_wind_direction(self):
        """
        Returns the vertical wind direction in degrees (processed)
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 3], cursor=self.__cursor)

    @property
    def wind_velocities(self):
        """
        Returns the horizontal wind velocity vector in m/s (processed)
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, -3:], cursor=self.__cursor)


if __name__ == '__main__':

    processor = AverageFilter()
    with Anemometer(window_length=5,
                    data_processor=processor,
                    log_file="out.csv") as sensor:
        time.sleep(0.5)
        for i in range(20):
            print(sensor.all_sensor_data)
            time.sleep(0.05)

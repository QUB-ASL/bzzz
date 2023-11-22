import serial
import numpy as np
from threading import Thread, Lock
import abc
import time
import datetime
import csv

class DataProcessor(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    def process(self, data, cursor=0):
        pass


class AverageFilter(DataProcessor):

    def __init__(self):
        super().__init__()

    def process(self, data):
        return np.nanmean(data, axis=0)


class MedianFilter(DataProcessor):

    def __init__(self):
        super().__init__()

    def process(self, data):
        return np.nanmedian(data, axis=0)


class NoFilter(DataProcessor):

    def __init__(self):
        super().__init__()

    def process(self, data, cursor):
        return data[cursor]

class DataLogger:

    def __init__(self, num_features, max_samples=1e4, feature_names=None):
        self.__data_vault = np.zeros((max_samples, num_features), dtype=np.float64)
        self.__cursor = 0
    
    def record(self, timespamp, datum):
        self.__data_vault[self.__cursor, :] = datum
        self.__cursor = self.__cursor + 1

    def save_to_csv(self, filename):
        with open(filename, "w") as fh:
            writer = csv.writer(fh)
            writer.writerows(self.__data_vault[:self.__cursor, :])


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
                 log_file=None):
        """
        Create a new instance of Anemometer

        :param serial_path: serial path; defaults to /dev/ttyS0 on RPi
        :param baud: baud rate of serial communication; defaults to 115200
        :param window_length: length of window of measurements; default: 3
        :param data_processor: data processor on buffer of measurements; default: MedianFilter()

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
        self.__timestamps_cache = np.array([datetime.datetime.now()] * self.__window_length)
        self.__cursor = 0
        self.__data_processor = data_processor
        self.__log_file = log_file
        if log_file is not None:
            self.__logger = DataLogger(num_features=7, max_samples=100000)
        self.__thread.start()

    def __get_measurements_in_background_t(self, serial_path, baud):
        """
        This is a thread that runs in the background to connect to the 
        serial and collect measurements, which are stored in a buffer
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
                    self.__timestamps_cache = datetime.datetime.now()
                    self.__values_cache[self.__cursor, :] = split_data_float                    
                    if self.__log_file is not None:
                        self.__logger.record(-1, self.__data_processor.process(self.__values_cache[:, :], cursor=self.__cursor))
                    self.__cursor = (self.__cursor + 1) % self.__window_length
                if not self.__keep_going:
                    ser.close()
                    return
                

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.__keep_going = False
        time.sleep(0.05)
        self.__logger.save_to_csv(self.__log_file)



    @property
    def all_sensor_data(self):
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, :])

    @property
    def wind_speed_3d(self):
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 0])

    @property
    def wind_speed_2d(self):
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 1])

    @property
    def horizontal_wind_direction(self):
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 2])

    @property
    def vertical_wind_direction(self):
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 3])

    @property
    def wind_velocities(self):
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, -3:])


if __name__ == '__main__':
    import time

    processor = NoFilter()
    with Anemometer(window_length=5, 
                    data_processor=processor, 
                    log_file="out.csv") as sensor:
        time.sleep(0.5)
        for i in range(15):
            print(sensor.all_sensor_data)
            time.sleep(0.05)
    

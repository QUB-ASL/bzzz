import serial
import numpy as np
from threading import Thread
import abc


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


class Anemometer:
    """
    Anemometer sensor

    This class is used to interface the anemometer
    """

    def __init__(self,
                 serial_path='/dev/ttyS0',
                 baud=115200,
                 window_length=3,
                 data_processor=MedianFilter()):
        """
        Create a new instance of Anemometer

        :param serial_path: serial path; defaults to /dev/ttyS0 on RPi
        :param baud: baud rate of serial communication; defaults to 115200
        :param window_length: length of window of measurements; default: 2
        :param data_processor: data processor on buffer of measurements

        Note: We assume that we receive 7 measurements from the anemometer
        """
        self.__thread = Thread(target=self.__get_measurements_in_background_t,
                               args=[serial_path, baud])
        self.__thread.start()
        self.__keep_going = True
        self.__window_length = window_length
        self.__values_cache = np.tile(np.nan, (self.__window_length, 7))
        self.__cursor = 0
        self.data_processor = data_processor

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
                self.__values_cache[self.__cursor, :] = split_data_float
                self.__cursor = (self.__cursor + 1) % self.__window_length
                if not self.__keep_going:
                    ser.close()
                    return

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.__keep_going = False

    @property
    def all_sensor_data(self):
        return self.data_processor.process(self.__values_cache)

    @property
    def wind_speed_3d(self):
        return self.data_processor.process(self.__values_cache[:, 0])

    @property
    def wind_speed_2d(self):
        return self.data_processor.process(self.__values_cache[:, 1])

    @property
    def horizontal_wind_direction(self):
        return self.data_processor.process(self.__values_cache[:, 2])

    @property
    def vertical_wind_direction(self):
        return self.data_processor.process(self.__values_cache[:, 3])

    @property
    def wind_velocities(self):
        return self.data_processor.process(self.__values_cache[:, -3:])


if __name__ == '__main__':
    import time

    processor = AverageFilter()
    with Anemometer(window_length=5, data_processor=processor) as sensor:
        time.sleep(0.5)
        for i in range(20):
            print(sensor.all_sensor_data)
            time.sleep(0.1)

    # The thread stops running once we exit the `with` block

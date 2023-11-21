import serial
import numpy as np
from threading import Thread


class Anemometer:

    def __init__(self, serial_path='/dev/ttyS0', baud=115200):
        thread = Thread(target=self.get_measurements_in_background,
                        args=[serial_path, baud])
        thread.start()
        self.__split_data_float = None
        self.__window_length = 5
        self.__values_cache = np.zeros((self.__window_length, 7))
        self.__cursor = 0

    def get_measurements_in_background(self, serial_path, baud):
        ser = serial.Serial(serial_path, baud, timeout=1)
        ser.reset_input_buffer()
        while True:
            if ser.in_waiting > 0:
                sensor_data = ser.readline().decode('utf-8').strip()
                split_data = sensor_data.split()
                self.__split_data_float = np.array(
                    [float(x) for x in split_data],
                    dtype=np.float64)
                self.__values_cache[self.__cursor, :] = self.__split_data_float
                self.__cursor = (self.__cursor + 1) % self.__window_length
                print(self.__values_cache)

    # @property
    # def all_sensor_data(self):
    #     if self.__split_data_float is not None:
    #         return self.__split_data_float

    # @property
    # def wind_speed_3d(self):
    #     if self.__split_data_float is not None:
    #         return self.__split_data_float[0]

    # @property
    # def wind_speed_2d(self):
    #     if self.__split_data_float is not None:
    #         return self.__split_data_float[1]

    # @property
    # def horizontal_wind_direction(self):
    #     if self.__split_data_float is not None:
    #         return self.__split_data_float[2]

    # @property
    # def vertical_wind_direction(self):
    #     if self.__split_data_float is not None:
    #         return self.__split_data_float[3]

    # @property
    # def wind_velocities(self):
    #     if self.__split_data_float is not None:
    #         return self.__split_data_float[-3:]

    # def update_sensor_data(self):
    #     current_all_sensor_data = self.__split_data_float
    #     if self.__split_data_float != self.__split_data_float:
    #         return self.__split_data_float


if __name__ == '__main__':
    sensor = Anemometer()
    # for i in range(10):
    #     sensor.get_measurements_in_background()
    #     x = sensor.all_sensor_data
    #     y = sensor.wind_velocities
    #     print(x)
    #     print(y)

import math
from filters import *
import smbus
import time
from ctypes import c_short
from threading import Thread, Lock
from data_logger import DataLogger
import datetime

def getShort(data, index):
    """
    Extract a signed 16-bit value from a data array starting at the specified index.
    :param data: A list or tuple containing byte data.
    :param index: The starting index in the data array.
    :return: A signed 16-bit integer value.
    """
    value = data[index] * 256 + data[index + 1]
    return value - 65536 if value > 32767 else value
class BMP180Sensor:
    def __init__(self, data_processor, window_length, DEVICE_ADDRESS=0x77, reference_pressure_at_sea_level=101325, log_file=None):
        self.daemon = True
        self.__lock = Lock()
        self.__thread = Thread(target=self.__get_measurements_in_background)
        self.window_length = window_length
        self.DEVICE_ADDRESS = DEVICE_ADDRESS
        self.bus = smbus.SMBus(1)
        self.data_processor = data_processor
        self.reference_pressure_at_sea_level = reference_pressure_at_sea_level
        self.__current_pressure = None
        self.__pressure_readings_list = []
        self.__current_altitude = None
        self.log_file = log_file
        if log_file is not None:
            feature_names = ("Date_Time", "Pressure", "Altitude")
            self.logger = DataLogger(num_features=2, feature_names=feature_names)
        self.__thread.start()
    def __get_measurements_in_background(self):
        while True:
            self.update_pressure()
            self.__calculate_altitude()
            if self.log_file is not None:
                current_timestamp = datetime.datetime.now()
                data_to_log = (self.__current_pressure, self.__current_altitude)
                self.logger.record(current_timestamp, data_to_log)
            time.sleep(0.5)  # Delay between measurements
    def update_pressure(self):
        with self.__lock:
            pressure_reading = self.get_pressure_measurement()
            self.__pressure_readings_list.append(pressure_reading)
            if len(self.__pressure_readings_list) > self.window_length:
                self.__pressure_readings_list.pop(0)
            self.__current_pressure = self.data_processor.process(self.__pressure_readings_list)

    def get_pressure_measurement(self):
        # Reading calibration data
        data = self.bus.read_i2c_block_data(self.DEVICE_ADDRESS, 0xAA, 22)

        # Converting calibration data
        AC1 = data[0] * 256 + data[1]
        if AC1 > 32767 :
            AC1 -= 65535
        AC2 = data[2] * 256 + data[3]
        if AC2 > 32767 :
            AC2 -= 65535
        AC3 = data[4] * 256 + data[5]
        if AC3 > 32767 :
            AC3 -= 65535
        AC4 = data[6] * 256 + data[7]
        AC5 = data[8] * 256 + data[9]
        AC6 = data[10] * 256 + data[11]
        B1 = data[12] * 256 + data[13]
        if B1 > 32767 :
            B1 -= 65535
        B2 = data[14] * 256 + data[15]
        if B2 > 32767 :
            B2 -= 65535
        MB = data[16] * 256 + data[17]
        if MB > 32767 :
            MB -= 65535
        MC = data[18] * 256 + data[19]
        if MC > 32767 :
            MC -= 65535
        MD = data[20] * 256 + data[21]
        if MD > 32767 :
            MD -= 65535
        # Reading raw temperature
        self.bus.write_byte_data(self.DEVICE_ADDRESS, 0xF4, 0x2E)
        time.sleep(0.005)
        data = self.bus.read_i2c_block_data(self.DEVICE_ADDRESS, 0xF6, 2)
        UT = data[0] * 256 + data[1]

        # Reading raw pressure
        self.bus.write_byte_data(self.DEVICE_ADDRESS, 0xF4, 0x74)
        time.sleep(0.026)
        data = self.bus.read_i2c_block_data(self.DEVICE_ADDRESS, 0xF6, 3)
        UP = ((data[0] * 65536) + (data[1] * 256) + data[2]) / 128

        # Calculating true temperature
        X1 = (UT - AC6) * AC5 / 32768.0
        X2 = (MC * 2048.0) / (X1 + MD)
        B5 = X1 + X2
        T = ((B5 + 8.0) / 16.0) / 10.0

        # Calculating true pressure
        B6 = B5 - 4000
        X1 = (B2 * (B6 * B6 / 4096.0)) / 2048.0
        X2 = AC2 * B6 / 2048.0
        X3 = X1 + X2
        B3 = (((AC1 * 4 + X3) * 2) + 2) / 4.0
        X1 = AC3 * B6 / 8192.0
        X2 = (B1 * (B6 * B6 / 2048.0)) / 65536.0
        X3 = ((X1 + X2) + 2) / 4.0
        B4 = AC4 * (X3 + 32768) / 32768.0
        B7 = ((UP - B3) * (25000.0))
        pressure = 0.0
        if B7 < 2147483648 :
            pressure = (B7 * 2) / B4
        else :
            pressure = (B7 / B4) * 2
        X1 = (pressure / 256.0) * (pressure / 256.0)
        X1 = (X1 * 3038.0) / 65536.0
        X2 = ((-7357) * pressure) / 65536.0
        pressure = (pressure + (X1 + X2 + 3791) / 16.0)
        return pressure

    def __calculate_altitude(self):
        with self.__lock:
            altitude = 44330 * (1 - pow((self.__current_pressure / self.reference_pressure_at_sea_level), 0.1903))
            self.__current_altitude = altitude

    def convert_to_signed(self, data):
        value = data[0] * 256 + data[1]
        if value > 32767:
            value -= 65536
        return value
    
    def convert_to_unsigned(self, data):
        return data[0] * 256 + data[1]
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__keep_going = False
        if self.log_file is not None:
            self.logger.save_to_csv(self.log_file)

if __name__ == "__main__":
    log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_BMP180Sensor.csv")
    processor = AverageFilter() 
    with BMP180Sensor(window_length=5, data_processor=processor, reference_pressure_at_sea_level=101325, log_file=log_filename) as sensor:
        time.sleep(600)  # Collect data for 10 minutes
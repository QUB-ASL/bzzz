from filters import MedianFilter
from filters import AverageFilter
import smbus
import time
from ctypes import c_short
import threading
from data_logger import DataLogger
import datetime
"""
This module defines a PressureSensor class that inherits from threading.Thread, enabling it to read and log pressure 
and altitude data in a separate thread. The class is designed to work with the BMP180 I2C digital barometric pressure sensor, 
commonly used with Raspberry Pi. The sensor's readings are processed through a filter (e.g., MedianFilter, AverageFilter) to
obtain smoothed values. The module also includes utility functions for data conversion and sensor calibration.

Classes:
    PressureSensor: Extends threading.Thread to continuously read pressure data from the BMP180 sensor, process the readings 
    through a specified filter, calculate altitude based on pressure, and log the results if a log file is specified.

Functions:
    _convertToString(data): Convert binary data into a string representation.
    _getShort(data, index): Extract a signed 16-bit value from a data array starting at the specified index.
    _getUshort(data, index): Extract an unsigned 16-bit value from a data array starting at the specified index.

Usage:
    To use the PressureSensor class, create an instance by specifying the data processing filter, window length for the filter, 
    device address of the sensor, reference pressure at sea level (optional), and log file name (optional). Call the start() method 
    to begin reading and processing data in a separate thread. Use the context manager syntax with the sensor object to automatically 
    start and stop the thread.
"""

# NOTE: below three functions below are adapted from https://www.raspberrypi-spy.co.uk/2015/04/bmp180-i2c-digital-barometric-pressure-sensor/
def _convertToString(data):
    """
    Convert binary data into a string representation.
    :param data: A list or tuple containing two bytes of data.
    :return: A string representation of the converted data.
    """
    return str((data[1] + (256 * data[0])) / 1.2)


def _getShort(data, index):
    """
    Extract a signed 16-bit value from a data array starting at the specified index.
    :param data: A list or tuple containing byte data.
    :param index: The starting index in the data array.
    :return: A signed 16-bit integer value.
    """
    return c_short((data[index] << 8) + data[index + 1]).value


def _getUshort(data, index):
    """
    Extract an unsigned 16-bit value from a data array starting at the specified index.
    :param data: A list or tuple containing byte data.
    :param index: The starting index in the data array.
    :return: An unsigned 16-bit integer value.
    """
    return (data[index] << 8) + data[index + 1]

class PressureSensor(threading.Thread):
    """
    A class for reading and logging pressure and altitude data from the BMP180 sensor in a separate thread.
    
    """

    def __init__(self, 
                 data_processor, 
                 window_length, 
                 DEVICE_ADDRESS=0x77, 
                 reference_pressure_at_sea_level=None, 
                 log_file=None):
        """
        Initialize the PressureSensor thread with the specified parameters.
        
        :param data_processor: An instance of a filter class for processing pressure readings.
        :param window_length: The number of readings to include in the moving window for filtering.
        :param DEVICE_ADDRESS: I2C address of the BMP180 sensor (default 0x77).
        :param reference_pressure_at_sea_level: Reference pressure at sea level used for altitude calculations (optional).
        :param log_file: Name of the file to log pressure and altitude readings (optional).
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.__lock = threading.Lock()
        # Sensor parameters
        self.window_length = window_length
        self.DEVICE_ADDRESS = DEVICE_ADDRESS
        self.smbus = smbus.SMBus(1)
        self.data_processor = data_processor  # Data processor object
        self.reference_pressure_at_sea_level = reference_pressure_at_sea_level

        # Data attributes
        self.__current_pressure = None
        self.__pressure_readings_list = []
        self.__current_altitude = None


        # Logger
        self.log_file = log_file
        if log_file is not None:
            feature_names = ("Date_Time", "Pressure", "Altitude")
            self.logger = DataLogger(num_features=2, 
                                     feature_names=feature_names)
        
        # Sensor initialization
        self.__init_pressure_sensor()
        self.stop_thread = threading.Event()

    def __init_pressure_sensor(self):
        """
        Initialize the pressure sensor by reading initial pressure values and setting up the reference pressure at sea level if not provided.
        """
        # Initialize pressure readings list with initial values
        for _ in range(self.window_length):
            self.__pressure_readings_list.append(self._get_current_pressure_measurement())

        # If reference pressure at sea level is not provided, calculate it using the data processor
        if self.reference_pressure_at_sea_level is None:
            self.reference_pressure_at_sea_level = self.data_processor.process(self.__pressure_readings_list)

        # Update the altitude based on the initial pressure readings
        self.update_altitude()


    # NOTE: adapted from https://www.raspberrypi-spy.co.uk/2015/04/bmp180-i2c-digital-barometric-pressure-sensor/
    def __readBmp180Id(self):
        """
        Read the chip ID and version from the BMP180 sensor.
        :return: A tuple containing the chip ID and chip version.
        """
        REG_ID = 0xD0
        chip_id, chip_version = self.smbus.read_i2c_block_data(
            self.DEVICE_ADDRESS, REG_ID, 2)
        return chip_id, chip_version

    # NOTE: adapted from https://www.raspberrypi-spy.co.uk/2015/04/bmp180-i2c-digital-barometric-pressure-sensor/
    def __readBmp180(self):
        """
        Read and process pressure and temperature data from the BMP180 sensor based on the device's calibration data.
        """
        # Register Addresses
        REG_CALIB = 0xAA
        REG_MEAS = 0xF4
        REG_MSB = 0xF6
        REG_LSB = 0xF7
        # Control Register Address
        CRV_TEMP = 0x2E
        CRV_PRES = 0x34
        # Oversample setting
        OVERSAMPLE = 3    # 0 - 3

        # Read calibration data
        # Read calibration data from EEPROM
        cal = self.smbus.read_i2c_block_data(
            self.DEVICE_ADDRESS, REG_CALIB, 22)

        # Convert byte data to word values
        AC1 = _getShort(cal, 0)
        AC2 = _getShort(cal, 2)
        AC3 = _getShort(cal, 4)
        AC4 = _getUshort(cal, 6)
        AC5 = _getUshort(cal, 8)
        AC6 = _getUshort(cal, 10)
        B1 = _getShort(cal, 12)
        B2 = _getShort(cal, 14)
        MB = _getShort(cal, 16)
        MC = _getShort(cal, 18)
        MD = _getShort(cal, 20)

        # Read temperature
        self.smbus.write_byte_data(self.DEVICE_ADDRESS, REG_MEAS, CRV_TEMP)
        time.sleep(0.005)
        (msb, lsb) = self.smbus.read_i2c_block_data(
            self.DEVICE_ADDRESS, REG_MSB, 2)
        UT = (msb << 8) + lsb

        # Read pressure
        self.smbus.write_byte_data(
            self.DEVICE_ADDRESS, REG_MEAS, CRV_PRES + (OVERSAMPLE << 6))
        time.sleep(0.04)
        (msb, lsb, xsb) = self.smbus.read_i2c_block_data(
            self.DEVICE_ADDRESS, REG_MSB, 3)
        UP = ((msb << 16) + (lsb << 8) + xsb) >> (8 - OVERSAMPLE)

        # Refine temperature
        X1 = ((UT - AC6) * AC5) >> 15
        X2 = (MC << 11) / (X1 + MD)
        B5 = X1 + X2
        self.__temperature = int(B5 + 8) >> 4

        # Refine pressure
        B6 = B5 - 4000
        B62 = int(B6 * B6) >> 12
        X1 = (B2 * B62) >> 11
        X2 = int(AC2 * B6) >> 11
        X3 = X1 + X2
        B3 = (((AC1 * 4 + X3) << OVERSAMPLE) + 2) >> 2

        X1 = int(AC3 * B6) >> 13
        X2 = (B1 * B62) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = (AC4 * (X3 + 32768)) >> 15
        B7 = (UP - B3) * (50000 >> OVERSAMPLE)

        P = (B7 * 2) / B4

        X1 = (int(P) >> 8) * (int(P) >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = int(-7357 * P) >> 16
        self.__pressure = int(P + ((X1 + X2 + 3791) >> 4))

    @property
    def pressure(self):
        """
        Return the current pressure reading.
        :return: The current pressure in Pa.
        """
        return self.__current_pressure

    
    @property
    def altitude(self):
        """
        Return the current altitude calculation based on the current pressure and reference pressure at sea level.
        :return: The current altitude in meters.
        """
        return self.__current_altitude

   

    def _get_current_pressure_measurement(self):
        """
        Read the current pressure measurement from the sensor.
        :return: The current pressure reading in Pa.
        """
        self.__readBmp180()
        pressure_reading = self.__pressure
        return pressure_reading

    def _update_pressure(self):
        """
        Update the pressure reading list with a new measurement and process the readings through the specified filter.
        """
        with self.__lock:
            # Get current pressure measurement and add to readings list
            pressure_reading = self._get_current_pressure_measurement()
            self.__pressure_readings_list.append(pressure_reading)
            # Remove the oldest reading to maintain the buffer size
            if len(self.__pressure_readings_list) > self.window_length:
                self.__pressure_readings_list.pop(0)
            # Use the data processor to calculate the current pressure
            self.__current_pressure = self.data_processor.process(self.__pressure_readings_list)
        
    def _calculate_altitude_from_pressure(self):
        """
        Calculate the current altitude based on the current pressure reading and the reference pressure at sea level.
        """
        with self.__lock:
            # check calculate altitude from pressure
            self.__current_altitude = 44330 * \
                (1 - (self.__current_pressure/self.reference_pressure_at_sea_level)**(1/5.255))

    def update_altitude(self):
        """
        Update the current pressure reading and calculate the current altitude.
        """
        self._update_pressure()
        self._calculate_altitude_from_pressure()

    def run(self):
        """
        Override the threading.Thread.run method to continuously update altitude and log data if a log file is specified.
        """
        while not self.stop_thread.is_set():
            self.update_altitude()
            
            if self.log_file is not None:
                
                current_timestamp = datetime.datetime.now()
                data_to_log = (self.pressure, self.altitude)
                self.logger.record(current_timestamp, data_to_log)
                time.sleep(0.5)

    def stop(self):
        """
        Set the stop flag for the thread and save logged data to a CSV file if logging is enabled.
        """
        self.stop_thread.set()
        if self.log_file is not None:
            self.logger.save_to_csv(self.log_file)

    def __enter__(self):
        """
        Support the context manager protocol for the PressureSensor class.
        :return: The PressureSensor instance.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Support the context manager protocol for the PressureSensor class by stopping the thread on exit.
        """
        self.stop()

if __name__ == "__main__":
   
    log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_PressureSensor.csv")
    processor = AverageFilter()  # You need to define this class based on your requirements
    psensor = PressureSensor(window_length=100, data_processor=processor, reference_pressure_at_sea_level=102500, log_file=log_filename)
    psensor.start()
    with psensor:
        time.sleep(60)  # Collect data for 60 seconds
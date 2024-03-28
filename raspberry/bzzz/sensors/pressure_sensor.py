import math
import smbus
import time
from ctypes import c_short
from threading import Thread, Lock
from .data_logger import DataLogger
from .filters import *
import datetime

def _calculate_altitude_from_pressure(pres, temp, initial_pressure):
    """
    Calculate altitude from pressure and temperature using the barometric formula.

    :param pres: Measured pressure
    :param temp: Measured temperature in Celsius
    :param initial_pressure: 
    :return: Calculated altitude in meters
    """
    k = 1.380649e-23 #Boltzmann's Number
    molecular_mass = 4.8e-26 #mass of one molecule of air 
    g = 9.81 #gravity
    celsius_to_kelvin = 273.15 # constant for changing from celsius to Kelvin
    alt = (((temp+celsius_to_kelvin)*k)/((molecular_mass)*g)) * math.log(initial_pressure/pres)
    return alt
    
class BMP180Sensor:
    """
    Interface for the BMP180 sensor to measure pressure and calculate altitude.
    """
    def __init__(self, 
                 data_processor=MedianFilter(), 
                 window_length=3, 
                 DEVICE_ADDRESS=0x77, 
                 log_file=None):
        """
        Initialize the BMP180 sensor object.
        
        :param data_processor: Object to process the data readings (default: MedianFilter)
        :param window_length: Number of readings to keep in the moving window (default: 3)
        :param DEVICE_ADDRESS: I2C address of the BMP180 sensor (default: 0x77)
        :param initial_pressure: Reference pressure at sea level for altitude calculations (default: 101325 Pa)
        :param log_file: File path to log data readings (default: None)
        """
        self.__lock = Lock()
        self.__keep_running = True
        self.__thread = Thread(target=self.__get_measurements_in_background)
        self.__window_length = window_length
        self.__values_cache = np.tile(np.nan, (self.__window_length, 2))
        self.__cursor = 0
        self.__DEVICE_ADDRESS = DEVICE_ADDRESS
        self.__bus = smbus.SMBus(1)
        self.__data_processor = data_processor
                
        self.__log_file = log_file
        if self.__log_file is not None:
            feature_names = ("Date_Time", "Pressure", "Altitude")
            self.__logger = DataLogger(num_features=2, feature_names=feature_names)
        self.__thread.start()
        self.__initial_pressure = -1
        self.__initial_pressure = self.__initialise()
    
    def __get_measurements_in_background(self):
        """
        Thread method to continuously read measurements from the sensor, process them, and log them.
        """
        while self.__keep_running:
            pres, temp = self.__pressure_temp_from_sensor()
            alt = _calculate_altitude_from_pressure(pres, temp, self.__initial_pressure) if self.__initial_pressure > 0 else 0
            self.__values_cache[self.__cursor, :] = np.array([pres, alt])
            self.__cursor = (self.__cursor + 1) % self.__window_length
            if self.__log_file is not None:
                current_timestamp = datetime.datetime.now()
                data_to_log = (pres, alt)
                self.__logger.record(current_timestamp, data_to_log)  

    def pressure(self):
        """
        Get the current pressure reading, processed through the data processor.
        :return: Processed pressure reading
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, :], cursor=self.__cursor)[0]
    
    def altitude(self):
        """
        Get the current altitude reading, processed through the data processor.
        :return: Processed altitude reading
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, :], cursor=self.__cursor)[1]

    def __pressure_temp_from_sensor(self):
        """
        Read raw pressure and temperature data from the BMP180 sensor.

        This method communicates with the BMP180 sensor over the I2C bus to fetch the raw
        temperature and pressure readings. It then uses the sensor's calibration data to
        convert these raw readings into true temperature (in Celsius) and pressure (in Pa)
        values based on the sensor's calibration coefficients.

        The method handles the entire process of sending the correct commands to the sensor,
        reading the raw data, and applying the necessary conversion formulas as outlined
        in the BMP180 datasheet.

        :return: A tuple containing the true pressure (in Pa) and temperature (in Celsius).
        """
        # Reading calibration data
        data = self.__bus.read_i2c_block_data(self.__DEVICE_ADDRESS, 0xAA, 22)

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
        self.__bus.write_byte_data(self.__DEVICE_ADDRESS, 0xF4, 0x2E)
        time.sleep(0.005)
        data = self.__bus.read_i2c_block_data(self.__DEVICE_ADDRESS, 0xF6, 2)
        UT = data[0] * 256 + data[1]

        # Reading raw pressure
        self.__bus.write_byte_data(self.__DEVICE_ADDRESS, 0xF4, 0x74)
        time.sleep(0.026)
        data = self.__bus.read_i2c_block_data(self.__DEVICE_ADDRESS, 0xF6, 3)
        UP = ((data[0] * 65536) + (data[1] * 256) + data[2]) / 128

        # Calculating true temperature
        X1 = (UT - AC6) * AC5 / 32768.0
        X2 = (MC * 2048.0) / (X1 + MD)
        B5 = X1 + X2
        Temperature = ((B5 + 8.0) / 16.0) / 10.0

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
        return pressure, Temperature
              
            
    def __initialise(self, num_initial_readings=30):
        """
        Initialise the altitude by averaging the first few readings.
        :param num_initial_readings: Number of readings to average for initial altitude.
        """        
        sum_pressures = 0
        do_run = True
        idx_valid_measurements = 0
        idx_attempts = 0
        max_attempts = 4*num_initial_readings
        time.sleep(3)
        while do_run:
            p = self.pressure()
            if not np.isnan(p):
                sum_pressures += p
                idx_valid_measurements += 1
            if idx_valid_measurements == num_initial_readings:
                break
            time.sleep(0.2)
            idx_attempts += 1
            if idx_attempts >= max_attempts:
                raise Exception("Barometer initialisation took too long (too many nan's)")
        av_pressure = sum_pressures / num_initial_readings
        return av_pressure
        
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__keep_running = False
        if self.__log_file is not None:
            self.__logger.save_to_csv(self.__log_file)

if __name__ == "__main__":
    log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_BMP180Sensor.csv")
    processor = AverageFilter()
    with BMP180Sensor(window_length=5, log_file=log_filename) as sensor:
        for i in range(100):
            print(sensor.altitude())
            time.sleep(0.1)

        
# TODO: implement proper code for a particular sensor
# TODO: add proper Doc strings
# NOTE: for now, we are just passing dummy values
# TODO: review this file later

from filters import median_filter
import smbus
import time
from ctypes import c_short
import threading
from data_logger import DataLogger
from filters import NoFilter
import datetime
# NOTE: below three functions are adapted from https://www.raspberrypi-spy.co.uk/2015/04/bmp180-i2c-digital-barometric-pressure-sensor/
def _convertToString(data):
    # Simple function to convert binary data into
    # a string
    return str((data[1] + (256 * data[0])) / 1.2)


def _getShort(data, index):
    # return two bytes from data as a signed 16-bit value
    return c_short((data[index] << 8) + data[index + 1]).value


def _getUshort(data, index):
    # return two bytes from data as an unsigned 16-bit value
    return (data[index] << 8) + data[index + 1]

class PressureSensor(threading.Thread):
    def __init__(self, DEVICE_ADDRESS=0x77, median_filter_length=5, 
                 reference_pressure_at_sea_level=None, log_file=None):
        threading.Thread.__init__(self)
        self.daemon = True

        # Sensor parameters
        self.DEVICE_ADDRESS = DEVICE_ADDRESS
        self.smbus = smbus.SMBus(1)
        self._median_filter_length = median_filter_length
        self.reference_pressure_at_sea_level = reference_pressure_at_sea_level

        # Data attributes
        self.__current_pressure = None
        self.__previous_pressure = None
        self.__pressure_readings_list = [0] * median_filter_length  # Initialize with zeroes or a default value
        self.__pressure_readings_list_current_index = 0
        self.__current_altitude = None
        self._previous_altitude = None

        # Logger
        self.log_file = log_file
        if log_file is not None:
            feature_names = ("Date_Time", "Pressure", "Altitude")
            self.logger = DataLogger(num_features=2, 
                                     feature_names=feature_names)
        
        # Sensor initialization
        self._init_pressure_sensor()
        self.stop_thread = threading.Event()

    def _init_pressure_sensor(self):
        
        for i in range(self._median_filter_length):
            self.__pressure_readings_list[i] = self._get_current_pressure_measurement()

        # If reference pressure at sea level is not provided, calculate it
        if self.reference_pressure_at_sea_level is None:
            self.reference_pressure_at_sea_level = median_filter(self.__pressure_readings_list)

        # Update the altitude based on the initial pressure readings
        self.update_altitude()

    # NOTE: adapted from https://www.raspberrypi-spy.co.uk/2015/04/bmp180-i2c-digital-barometric-pressure-sensor/
    def __readBmp180Id(self):
        # Chip ID Register Address
        REG_ID = 0xD0
        chip_id, chip_version = self.smbus.read_i2c_block_data(
            self.DEVICE_ADDRESS, REG_ID, 2)
        return chip_id, chip_version

    # NOTE: adapted from https://www.raspberrypi-spy.co.uk/2015/04/bmp180-i2c-digital-barometric-pressure-sensor/
    def __readBmp180(self):
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
        return self.__current_pressure

    
    @property
    def altitude(self):
        return self.__current_altitude

   

    def _get_current_pressure_measurement(self):
        # TODO: add code to get measurement from sensor
        self.__readBmp180()
        pressure_reading = self.__pressure
        return pressure_reading

    def _update_pressure(self):
        
        pressure_reading = self._get_current_pressure_measurement()
        self.__previous_pressure = self.__current_pressure
        self.__pressure_readings_list[self.__pressure_readings_list_current_index] = pressure_reading
        if 0 <= self.__pressure_readings_list_current_index < self._median_filter_length - 1:
            self.__pressure_readings_list_current_index += 1
        else:
            self.__pressure_readings_list_current_index = 0
        self.__current_pressure = median_filter(
            self.__pressure_readings_list, self._median_filter_length)
        
    def _calculate_altitude_from_pressure(self):
        
        # check calculate altitude from pressure
        self.__current_altitude = 44330 * \
            (1 - (self.__current_pressure/self.reference_pressure_at_sea_level)**(1/5.255))

    def update_altitude(self):
        self._update_pressure()
        self._calculate_altitude_from_pressure()

    def run(self):
        
        while not self.stop_thread.is_set():
            self.update_altitude()
            
            if self.log_file is not None:
                
                current_timestamp = datetime.datetime.now()
                data_to_log = (self.pressure, self.altitude)
                self.logger.record(current_timestamp, data_to_log)
                time.sleep(0.5)

    def stop(self):
        self.stop_thread.set()
        if self.log_file is not None:
            self.logger.save_to_csv(self.log_file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

if __name__ == "__main__":
    log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_PressureSensor.csv")
    psensor = PressureSensor(reference_pressure_at_sea_level=102500, log_file=log_filename)
    psensor.start()  # Start the thread
    with psensor:
        time.sleep(60)
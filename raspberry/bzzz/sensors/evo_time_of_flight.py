import serial
import crcmod.predefined
import numpy as np
from threading import Thread, Lock
import time
import datetime
from .data_logger import DataLogger
from .filters import *


def _distance_mapping(rng):
    # Checking error codes
    if rng == 65535:  # Sensor measuring above its maximum limit
        dec_out = float('nan')  # TOO FAR
    elif rng == 1:  # Sensor not able to measure
        dec_out = float('nan') # WHATEVER!
    elif rng == 0:  # Sensor detecting object below minimum range
        dec_out = -float('nan') # TOO CLOSE
    else:
        # Convert to meters
        dec_out = rng / 1000.0
    return dec_out


class EvoSensor:

    def __init__(self,
                 serial_path='/dev/ttyAMA2',
                 baud=115200,
                 window_length=3,
                 data_processor=NoFilter(),
                 log_file=None,
                 max_samples=100000):
        """
        Create a new instance of Evo time of flight sensor

        :param serial_path: serial path; defaults to /dev/ttyAMA2 (UART2) on RPi
        :param baud: baud rate of serial communication; defaults to 115200
        :param window_length: length of window of measurements; default: 3
        :param data_processor: data processor on buffer of measurements; default: NoFilter()
        :param log_file: file name to log data; default: None
        :param max_samples: maximum number of samples to record; default: 100000

        If `log_file` is None, the data is not logged; otherwise, on exit,
        the data are stored in a CSV file

        Note: We assume that we receive 1 distance measurement from 
              the Evo time of flight sensor
        """

        # A lock is used to guarantee that we won't be reading the data
        # while the thread in the background is writing it
        self.__lock = Lock()
        self.__thread = Thread(target=self.__get_measurements_in_background_t,
                               args=[serial_path, baud])
        self.__keep_going = True
        self.__window_length = window_length
        self.__values_cache = np.tile(np.nan, (self.__window_length, 1))
        self.__cursor = 0
        self.__logger_start_cursor = 0
        self.__data_processor = data_processor
        self.__log_file = log_file
        self.__max_samples = max_samples
        if log_file is not None:
            feature_names = ("Date_Time", "Altitude")
            self.__logger = DataLogger(num_features=1,
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
        crc8_fn = crcmod.predefined.mkPredefinedCrcFun('crc-8')
        ser = serial.Serial(serial_path, baud, timeout=1)
        ser.reset_input_buffer()
        
        while self.__keep_going:
            if ser.in_waiting > 0:
                data_header = ser.read(1)
                if data_header == b'T':
                    # After T read 3 bytes
                    frame = data_header + ser.read(3)
                    if frame[3] == crc8_fn(frame[0:3]):
                        # Convert binary frame to decimal in shifting by 8 the frame
                        rng = frame[1] << 8
                        rng = rng | (frame[2] & 0xFF)

                # Checking error codes
                dec_out = _distance_mapping(rng)

                self.__logger_start_cursor = self.__cursor
                with self.__lock:
                    self.__values_cache[self.__cursor, :] = dec_out
                    self.__cursor = (self.__cursor + 1) % self.__window_length                                    
                    if self.__log_file is not None \
                        and self.__logger_start_cursor < self.__max_samples:
                        current_timestamp = datetime.datetime.now()
                        self.__logger.record(current_timestamp, dec_out)
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
    def distance(self):
        """
        Returns the distance from the sensor in meters
        """
        with self.__lock:
            return self.__data_processor.process(
                self.__values_cache[:, 0:], cursor=self.__cursor)


if __name__ == "__main__":

    filename = datetime.datetime.now().strftime("EVO-%d-%m-%y--%H-%M.csv")
    processor = MedianFilter()
    with EvoSensor(window_length=3,
                   data_processor=processor,
                   log_file=filename) as sensor:
        for i in range(20000):
            print(sensor.distance)
        # set time for how long you want to record data for in seconds
        time.sleep(0.1)

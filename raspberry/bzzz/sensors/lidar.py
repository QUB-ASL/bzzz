from threading import Thread, Lock
from data_logger import DataLogger
from rplidar import RPLidar
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani

class lidar:
    """
    LiDAR Module

    This class is used to interface the LiDAR Module
    """

    def __init__(self,
                 serial_path="/dev/ttyUSB0",
                 baud=115200,
                 scan_type="normal",
                 log_file=None,
                 max_samples=100000,
                 scan_size=400,
                 window_length=3):
        """
        Initialises LiDAR interface object
        :param serial_path: Path to the serial port where the LiDAR is
                            connected; default: "/dev/ttyUSB0"
        :param baud: baud rate of serial communication; defaults to 115200
        :param scan_type: type of communication protocol; can be "normal"
                            or "express"; default: "normal"
        :param log_file: File name to log data; default: None
        :param max_samples: maximum number of samples to record; default:
            100000
        :param scan_size: number of measurements per scan; default: 100
        :param window_length: number of scans to be stored; default: 3

        If `log_file` is None, the data is not logged; otherwise, on exit,
        the data are stored in a CSV file
        """

        self.__serial_path = serial_path
        self.__baud = baud
        self.__window_length = window_length
        self.__scan_size = scan_size
        self.__scan_type = scan_type
        # There are three values per measurement: Quality, Angle, and Range
        self.__values_cache = np.tile(np.nan, (self.__window_length, self.__scan_size, 3))
        self.__cursor = 0
        self.__log_file = log_file
        self.__max_samples = max_samples
        self.__driver = RPLidar(port=self.__serial_path,
                                baudrate=self.__baud)
        self.__iterator = None
        #self.__lock = Lock()
        self.__thread = Thread(target=self.__get_scans_in_background,args=[self.__scan_type,self.__scan_size])
        self.__keep_going = True

        if log_file is not None:
            feature_names = ("Date_time", "Quality", "Angle", "Distance")
            self.__logger = DataLogger(num_features=4,
                                       max_samples=max_samples,
                                       feature_names=feature_names)
        self.__thread.start()
        #self.__iterator = self.__driver.iter_scans(self.__scan_type, self.__scan_size, min_len=20)
    def __get_scans_in_background(self,scan_type,max_buf_meas):
        self.__iterator = self.__driver.iter_scans(scan_type, max_buf_meas, min_len=10)


    '''
    def __get_scans_in_background(self,scan_type,max_buf_meas):
        """
        Continuously reads incoming LiDAR data from the USB serial connection.
        These are stored in the __values_cache buffer array.
        """
        iterator = self.__driver.iter_scans(scan_type, max_buf_meas, min_len=20)
        while self.__keep_going:
            time.sleep(1)# Gives "attempting to use port that is not open" error
            with self.__lock:
                self.__cursor = ((self.__cursor + 1) % self.__window_length)
                current_scan = next(iterator)
                self.__values_cache[self.__cursor, 0:len(current_scan), :] = current_scan
                if (self.__log_file is not None 
                    and self.__cursor < self.__max_samples):
                    current_timestamp = datetime.datetime.now()
                    for measurement in current_scan:
                        self.__logger.record(current_timestamp, measurement)

                self.__cursor = ((self.__cursor + 1) % self.__window_length)
            if not self.__keep_going:
                return
    '''

    def __enter__(self):
        return self


    def __exit__(self, *args):
        self.__keep_going = False
        self.__driver.stop()
        self.__driver.disconnect()
        #self.__thread.join()
        if self.__log_file is not None:
            self.__logger.save_to_csv(self.__log_file)


    @property
    def scan(self):
        """
        Returns latest LiDAR scan in the __values_cache buffer.
        """
        return next(self.__iterator)
        #with self.__lock:# this fails to get the lock for some reason
        #    return self.__values_cache[((self.__cursor) % self.__window_length), :, :]


if __name__ == "__main__":
    filename = datetime.datetime.now().strftime("Lidar_%d-%m-%y--%H-%M.csv")
    with lidar(scan_type="express", log_file=filename) as lidar_obj:
        while True:
            scan = lidar_obj.scan
            print(scan)

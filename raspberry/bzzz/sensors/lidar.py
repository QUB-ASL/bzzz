from threading import Thread, Lock
from .data_logger import DataLogger
from rplidar import RPLidar
import datetime
import numpy as np

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
                 scan_size=600):
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

        If `log_file` is None, the data is not logged; otherwise, on exit,
        the data is stored in a CSV file
        """

        self.__serial_path = serial_path
        self.__baud = baud
        self.__window_length = window_length
        self.__scan_size = scan_size
        self.__scan_type = scan_type
        self.__log_file = log_file
        self.__max_samples = max_samples
        self.__driver = RPLidar(port=self.__serial_path,
                                baudrate=self.__baud)
        self.__iterator = None
        self.__thread = Thread(target=self.__get_scans_in_background,args=[self.__scan_type,self.__scan_size])
        self.__keep_going = True

        if log_file is not None:
            feature_names = ("Date_time", "Quality", "Angle", "Distance")
            self.__logger = DataLogger(num_features=3,
                                       max_samples=max_samples,
                                       feature_names=feature_names)
        self.__thread.start()


    def __get_scans_in_background(self,scan_type,max_buf_meas):
        self.__iterator = self.__driver.iter_scans(scan_type, max_buf_meas, min_len=10)


    def __enter__(self):
        return self


    def __exit__(self, *args):
        self.__keep_going = False
        self.__thread.join()
        self.__driver.stop()
        self.__driver.disconnect()
        if self.__log_file is not None:
            self.__logger.save_to_csv(self.__log_file)


    @property
    def scan(self):
        """
        Returns latest LiDAR scan in the __values_cache buffer.
        """
        next_scan = next(self.__iterator)
        if self.__log_file is not None:
            self.__logger.record_series(datetime.datetime.now(),np.asarray(next_scan))
        return next_scan


if __name__ == "__main__":
    filename = datetime.datetime.now().strftime("Lidar_%d-%m-%y--%H-%M.csv")
    with lidar(scan_type="express", log_file=filename) as lidar_obj:
        while True:
            scan = lidar_obj.scan
            length = len(scan)
            measures = [(measure[1],measure[2]) for measure in scan]
            print(measures, "\n Length:", length)

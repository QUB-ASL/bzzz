import serial
import time
from threading import Thread, Lock
import csv
from datetime import datetime, timedelta

def deg_min_sec_to_decimal(degrees, minutes, direction):
    """
    Convert degrees-minutes-seconds from GNGLL to decimal

    :param degrees: degrees
    :param minutes: minutes
    :param direction: direction (can be one of 'N', 'W', 'E', 'S')
    :return: decimal representation of GPS coordinates
    """
    decimal_degrees = degrees + minutes / 60
    if direction in ['S', 'W']:  # need to be denoted with a negative value
        decimal_degrees *= -1
    return decimal_degrees

class GpsLogger:
    """
    Handles logging GPS data to a CSV file

    :param filename: Name of the file to save the data
    :param max_samples: Maximum number of data samples to log
    """
    def __init__(self, filename, max_samples=100000):
        self.filename = filename
        self.max_samples = max_samples
        self.samples = []

    def log(self, timestamp, latitude, longitude, altitude):
        """
        Logs a single sample of GPS data

        :param timestamp: The timestamp of the data sample
        :param latitude: Latitude in decimal degrees
        :param longitude: Longitude in decimal degrees
        :param altitude: Altitude in meters
        """
        if len(self.samples) < self.max_samples:
            self.samples.append([timestamp, latitude, longitude, altitude])

    def save_to_csv(self):
        """
        Saves all logged data to a CSV file
        """
        with open(self.filename, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Latitude", "Longitude", "Altitude"])  # Header row for CSV
            writer.writerows(self.samples)
        
class Gps:
    """
    Initializes the GPS data handler with the default serial path and baud rate,
    sets up storage for latitude, longitude, and altitude,
    and starts a background thread to continuously read and parse GPS data.

    :param serial_path: Path to the serial port where the GPS is connected
                        (default: "/dev/ttyACM0")
    :param baud: Baud rate for the serial connection (default: 500000)
    :param log_file: Name of the file to log GPS data (default: "gps_data.csv")
    """
    def __init__(self, serial_path="/dev/ttyACM0", baud=500000, log_file="gps_data.csv"):
        self.__lock = Lock()
        self.__gpgll_latitude = None
        self.__gpgll_longitude = None
        self.__gpgsv_altitude = None
        self.logger = GpsLogger(log_file)
        self.__thread = Thread(target=self.__get_measurements_in_background_t, args=[serial_path, baud])
        self.__keep_going = True
        self.__thread.start()

    def __get_measurements_in_background_t(self, serial_path, baud):
        """
        Continuously reads GPS data from the serial port, parsing GNGLL messages
        for latitude and longitude, and GPGSV messages for altitude,
        updating the object's GPS attributes accordingly. This method will write
        the GPS data to a CSV file for 2 minutes.

        :param serial_path: Serial port path
        :param baud: Baud rate for the serial connection
        """
        stop_time = datetime.now() + timedelta(minutes=2)  # Determine when to stop collecting data
        with serial.Serial(serial_path, baud, timeout=1) as ser:
            while datetime.now() < stop_time and self.__keep_going:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', 'ignore').strip()  # use ignore when the code come across undecodable bytes
                    tokens = line.split(",")
                    msg_key = tokens[0]

                    if msg_key == "$GNGLL" and tokens[1] and tokens[3]:
                        lat_deg = int(float(tokens[1]) / 100)
                        lat_min = float(tokens[1]) % 100
                        latitude = deg_min_sec_to_decimal(lat_deg, lat_min, tokens[2])

                        lon_deg = int(float(tokens[3]) / 100)
                        lon_min = float(tokens[3]) % 100
                        longitude = deg_min_sec_to_decimal(lon_deg, lon_min, tokens[4])

                        with self.__lock:
                            self.__gpgll_latitude = latitude
                            self.__gpgll_longitude = longitude

                    elif msg_key == "$GPGSV" and len(tokens) > 5:
                        altitude = float(tokens[5])
                        with self.__lock:
                            self.__gpgsv_altitude = altitude

                    with self.__lock:
                        if self.__gpgll_latitude is not None and self.__gpgll_longitude is not None and self.__gpgsv_altitude is not None:
                            self.logger.log(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.__gpgll_latitude, self.__gpgll_longitude, self.__gpgsv_altitude)
    
            
    def __enter__(self):
        """
        Enables the GPS object to be used with the 'with' statement for context management
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Ensures the background thread is stopped and the GPS data is saved when exiting the context
        """
        self.__keep_going = False
        self.__thread.join()  # Ensure background thread has finished
        self.logger.save_to_csv()  # Save collected data to CSV

    @property
    def latitude(self):
        """
        Latitude in decimal degrees
        """
        with self.__lock:
            return self.__gpgll_latitude

    @property
    def longitude(self):
        """
        Longitude in decimal degrees
        """
        with self.__lock:
            return self.__gpgll_longitude

    @property
    def altitude(self):
        """
        Altitude in meters
        """
        with self.__lock:
            return self.__gpgsv_altitude

if __name__ == "__main__":
    with Gps() as gps:
        time.sleep(120)  # Collect data for 2 minutes





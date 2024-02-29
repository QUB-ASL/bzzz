import serial
import time
from threading import Thread
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

class Gps:

    def __init__(self, serial_path="/dev/tty.usbmodem14201", baud=500000):
        """
        Initializes the GPS data handler with the default serial path and baud rate, 
        sets up storage for latitude, longitude, and altitude, 
        and starts a background thread to continuously read and parse GPS data.

        :param serial_path: Path to the serial port where the GPS is connected 
                            (default: "/dev/tty.usbmodem14201")
        :param baud: Baud rate for the serial connection (default: 500000)
        """
        self.__gpgll_latitude = None
        self.__gpgll_longitude = None
        self.__gpgsv_altitude = None

        self.__thread = Thread(target=self.__get_measurements_in_background_t, args=[serial_path, baud])
        self.__thread.daemon = True  # Ensure thread does not prevent program termination
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
        with serial.Serial(serial_path, baud, timeout=1) as ser, open("gps_data.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Latitude", "Longitude", "Altitude"])  # Header row for CSV

            while datetime.now() < stop_time:  # Collect and write data for 2 minutes
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', 'ignore').strip() # use ignore when the code come accross undecodable bytes
                    tokens = line.split(",")
                    msg_key = tokens[0]

                    if msg_key == "$GNGLL" and tokens[1] and tokens[3]:
                        lat_deg = int(float(tokens[1]) / 100)
                        lat_min = float(tokens[1]) % 100
                        latitude = deg_min_sec_to_decimal(lat_deg, lat_min, tokens[2])

                        lon_deg = int(float(tokens[3]) / 100)
                        lon_min = float(tokens[3]) % 100
                        longitude = deg_min_sec_to_decimal(lon_deg, lon_min, tokens[4])

                        self.__gpgll_latitude = latitude
                        self.__gpgll_longitude = longitude

                    elif msg_key == "$GPGSV" and len(tokens) > 5:
                        altitude = float(tokens[5])
                        self.__gpgsv_altitude = altitude

                    # Only write to CSV if all data is present
                    if self.__gpgll_latitude is not None and self.__gpgll_longitude is not None and self.__gpgsv_altitude is not None:
                        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.__gpgll_latitude, self.__gpgll_longitude, self.__gpgsv_altitude])

    @property
    def latitude(self):
        """
        Latitude in decimal degrees
        """
        return self.__gpgll_latitude

    @property
    def longitude(self):
        """
        Longitude in decimal degrees
        """
        return self.__gpgll_longitude

    @property
    def altitude(self):
        """
        Altitude in meters
        """
        return self.__gpgsv_altitude

if __name__ == "__main__":
    gps = Gps()  # Using default serial path and baud rate
    time.sleep(120)  # Keep the main program running for 2 minutes



# from math import degrees
# import serial
# import time
# from threading import Thread
# import numpy as np


# def deg_min_sec_to_decimal(degrees,
#                            minutes,
#                            direction):
#     """
#     Convert degrees-minutes-seconds from GNGLL to decimal

#     :param degrees: degrees
#     :param minutes: minutes
#     :param dir: direction (can be one of 'N', 'W', 'E', 'S')
#     :return: decimal representation of GPS coordinates
#     """
#     decimal_degrees = degrees + minutes / 60
#     if direction in ['S', 'W']:  # need to be denoted with a negative value
#         decimal_degrees *= -1
#     return decimal_degrees


# class Gps:

#     def __init__(self,
#                  serial_path="/dev/ttyACM0",
#                  baud=500000):
#         """
#         Initialises the GPS data handler with default serial path and baud rate, 
#         sets up storage for latitude, longitude, and altitude, 
#         and starts a background thread to continuously read and parse GPS data.

#         :param serial_path: path to serial where GPS is connected 
#                             (default: "/dev/ttyACM0")
#         :param baud: BAUD rate of serial (default: 500000)
#         """
#         # Initialise objects to store various measurements
#         self.__gpgll_latitude = None
#         self.__gpgll_longitude = None
#         self.__gpgsv_altitude = None

#         self.__thread = Thread(target=self.__get_measurements_in_background_t,
#                                args=[serial_path, baud])
#         self.__thread.start()

#     def __get_measurements_in_background_t(self, serial_path, baud):
#         """
#         Continuously reads GPS data from a serial port, parses GNGLL messages
#         for latitude and longitude, and GPGSV messages for altitude, 
#         updating the object's GPS attributes accordingly.
#         """
#         ser = serial.Serial(serial_path, baud, timeout=1)
#         ser.reset_input_buffer()
#         while True:
#             if ser.in_waiting > 0:
#                 try:
#                     # Reads and cleans a line of serial data, splits it by
#                     # commas, and assigns the first value as a message key
#                     sensor_data = ser.readline().decode('utf-8').strip()
#                     tokens = sensor_data.split(",")
#                     msg_key = tokens[0]

#                     if msg_key == "$GNGLL":
#                         latitude = None
#                         longitude = None
#                         if tokens[1] and tokens[3]:
#                             # parsing GNGLL data to decimal
#                             lat_deg = int(float(tokens[1]) / 100)
#                             lat_min = float(tokens[1]) % 100
#                             latitude = deg_min_sec_to_decimal(
#                                 lat_deg, lat_min, tokens[2])

#                             lon_deg = int(float(tokens[3]) / 100)
#                             lon_min = float(tokens[3]) % 100
#                             longitude = deg_min_sec_to_decimal(
#                                 lon_deg, lon_min, tokens[4])

#                         # Update GPS data with the new values
#                         self.__gpgll_longitude = longitude
#                         self.__gpgll_latitude = latitude

#                     elif msg_key == "$GPGSV":  # parse gpgsv data
#                         altitude = float(tokens[5])
#                     # Update GPS data with the new values
#                     self.__gpgsv_altitude = altitude

#                 except Exception as e:
#                     print(f"Error processing GPS data: {e}")

#     @property
#     def latitude(self):
#         """
#         Latitude in degrees
#         """
#         return self.__gpgll_latitude

#     @property
#     def longitude(self):
#         """
#         Longitutde in degrees
#         """
#         return self.__gpgll_longitude

#     @property
#     def altitude(self):
#         """
#         Altitude in meters
#         """
#         return self.__gpgsv_altitude


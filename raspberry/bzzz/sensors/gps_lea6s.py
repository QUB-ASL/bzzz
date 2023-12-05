from math import degrees
import serial
import datetime
import time
from threading import Thread, Lock
import numpy as np


def deg_min_sec_to_decimal(
    #dms, dir="N"
    degrees, minutes, direction
    ):
    """
    Convert degrees-minutes-seconds from GPGLL to degrees (deciman)

    :param dms: degrees-minutes-seconds (must be positive)
    :param dir: direction (can be one of 'N', 'W', 'E', 'S')
    """
    
    decimal_degrees = degrees + minutes / 60
    if direction in ['S', 'W']:
        decimal_degrees *= -1
    return decimal_degrees

class GpsLea6SReader:

    def __init__(self,
                 serial_path="/dev/tty.usbmodem141301",
                 baud=500000):
        # Initialise objects to store various measurements
        self.__gpgll_latitude = None
        self.__gpgll_longitude = None
        self.__gpgsv_num_sats = None

        self.__thread = Thread(target=self.__get_measurements_in_background_t,
                               args=[serial_path, baud])
        self.__thread.start()

    def __get_measurements_in_background_t(self, serial_path, baud):
    
        ser = serial.Serial(serial_path, baud, timeout=1)
        ser.reset_input_buffer()
        while True:
            if ser.in_waiting > 0:
                try:
                    sensor_data = ser.readline().decode('utf-8').strip()
                    tokens = sensor_data.split(",")
                    msg_key = tokens[0]
                    
                    if msg_key == "$GPGLL":
                        latitude = None
                        longitude = None
                        if tokens[1] and tokens[3]:
                            lat_deg = int(float(tokens[1]) / 100)
                            lat_min = float(tokens[1]) % 100
                            latitude = deg_min_sec_to_decimal(lat_deg, lat_min, tokens[2])

                            lon_deg = int(float(tokens[3]) / 100)
                            lon_min = float(tokens[3]) % 100
                            longitude = deg_min_sec_to_decimal(lon_deg, lon_min, tokens[4])

                        # Update GPS data with the new values
                        self.__gpgll_longitude = longitude
                        self.__gpgll_latitude = latitude
                        
                        
                    elif msg_key == "$GPGSV": # parse gpgsv data
                        number_of_satellites = int(tokens[3])
                        altitude = float(tokens[5])
                    # Update GPS data with the new values
                    self.__gpgsv_num_sats = number_of_satellites
                    print(f"Processed GPGSV data: Number of Satellites = {number_of_satellites}, Altitude = {altitude}")

                        
                except Exception as e:
                    print(f"Error processing GPS data: {e}")


    @property
    def latitude(self):
        """
        GPS data object
        """
        return self.__gpgll_latitude

    @property
    def longitude(self):
        """
        GPS data object
        """
        return self.__gpgll_longitude

my_sensor = GpsLea6SReader(serial_path="/dev/tty.usbmodem141201")
while True:    
    lat = my_sensor.latitude
    lon = my_sensor.longitude
    print(f"{lat}, {lon}")
    time.sleep(1)
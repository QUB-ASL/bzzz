import serial
import time
from threading import Thread, Lock


class Gpll:

    def __init__(self):
        self.__latitude = None  # latitude in degrees (N is positive)
        self.__longitude = None
        self.__latitude_dir = None
        self.__longitude_dir = None
        self.__utc = None


class Gps:

    def __init__(self,
                 serial_path="/dev/tty.usbmodem14301",
                 baud=500000):
        # Initialise objects to store various measurements
        self.__gpll = Gpll()

        self.__thread = Thread(target=self.__get_measurements_in_background_t,
                               args=[serial_path, baud])
        self.__thread.start()

    def __get_measurements_in_background_t(self, serial_path, baud):
        ser = serial.Serial(serial_path, baud, timeout=1)
        ser.reset_input_buffer()
        while True:
            if ser.in_waiting > 0:
                sensor_data = ser.readline().decode('utf-8').strip()
                # self.__parse_gpll_data(sensor_data)
                if sensor_data.startswith("$GPGLL"):
                    tokens = sensor_data.split(",")
                    print(
                        f"{tokens[1]}{float(tokens[1])/100}, {float(tokens[3])/100}")


my_sensor = Gps()
print("Thread is running in background")
time.sleep(5)


# serial_path = "/dev/tty.usbmodem14301"
# baud = 500000

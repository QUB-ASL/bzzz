import serial
import numpy as np
from threading import Thread, Lock
import time
import datetime
from .data_logger import DataLogger
from .filters import *

#RELPOSNED and PVT
# Taken from https://github.com/mnltake/readF9P_UBX
def readUBX(readbytes):
    RELPOSNED = b'\x3c'
    POSLLH = b'\x02'
    
    j=0   
    while j < len(readbytes) : 
        i = 0
        payloadlength = 0
        ackPacket=[b'\xB5',b'\x62',b'\x01',b'\x00',b'\x00',b'\x00']
        while i < payloadlength +8:              
            if j < len(readbytes) :
                incoming_byte = readbytes[j]   
                j += 1
            else :
                break
            if (i < 3) and (incoming_byte == ackPacket[i]):
                i += 1
            elif i == 3:
                ackPacket[i]=incoming_byte
                i += 1              
            elif i == 4 :
                ackPacket[i]=incoming_byte
                i += 1
            elif i == 5 :
                ackPacket[i]=incoming_byte        
                payloadlength = int.from_bytes(ackPacket[4]+ackPacket[5], 
                                               byteorder='little',
                                               signed=False) 
                i += 1
            elif (i > 5) :
                ackPacket.append(incoming_byte)
                i += 1
        if checksum(ackPacket,payloadlength) :
            if ackPacket[3] == RELPOSNED:
                N, E, D, gnss_status, rtk_status= parseNED(ackPacket)
            elif ackPacket[3] == POSLLH:
                Lon, Lat, Height, hMSL = parseLLH(ackPacket)
    return N, E, D, gnss_status, rtk_status, Lon, Lat, Height, hMSL

def checksum(ackPacket, payloadlength):
    CK_A =0
    CK_B =0
    for i in range(2, payloadlength+ 6):
        CK_A = CK_A + int.from_bytes(ackPacket[i], byteorder='little',
                                     signed=False) 
        CK_B = CK_B +CK_A
    CK_A &=0xff
    CK_B &=0xff
    if ((CK_A ==  int.from_bytes(ackPacket[-2], byteorder='little',
                                 signed=False)) 
    and (CK_B ==  int.from_bytes(ackPacket[-1], byteorder='little',
                                 signed=False))):
        #print("ACK Received")
        return True
    else :
        print("ACK Checksum Failure:")  
        return False

def parseNED(ackPacket):
    #relPosN
    byteoffset =8 + 6
    bytevalue =  ackPacket[byteoffset] 
    for i in range(1,4):
        bytevalue  +=  ackPacket[byteoffset+i] 
    N = int.from_bytes(bytevalue, byteorder='little',signed=True)/100
    NH = int.from_bytes(ackPacket[32 + 6], byteorder='little',signed=True) 

    #relPosE
    byteoffset =12 + 6
    bytevalue = ackPacket[byteoffset] 
    for i in range(1,4):
        bytevalue  +=  ackPacket[byteoffset+i] 
    E = int.from_bytes(bytevalue, byteorder='little',signed=True)/100
    EH = int.from_bytes(ackPacket[33 + 6], byteorder='little',signed=True) 

    #relPosD
    byteoffset =16 + 6
    bytevalue = ackPacket[byteoffset] 
    for i in range(1,4):
        bytevalue  +=  ackPacket[byteoffset+i] 
    D = int.from_bytes(bytevalue, byteorder='little',signed=True)/100 
    DH = int.from_bytes(ackPacket[34 + 6], byteorder='little',signed=True)

    #Carrier solution status
    flags = int.from_bytes(ackPacket[60 + 6], byteorder='little',signed=True) 
    gnssFixOk =  flags  & (1 << 0) #gnssFixOK 
    carrSoln =  (flags   & (0b11 <<3)) >> 3 #carrSoln0:no carrier 1:float 2:fix

    #GNSS time
    byteoffset =4 + 6
    bytevalue = ackPacket[byteoffset] 
    for i in range(1,4):
        bytevalue  +=  ackPacket[byteoffset+i] 
    iTow = int.from_bytes(bytevalue, byteorder='little',signed=True) 

    #relPosLength
    byteoffset =20 + 6
    bytevalue = ackPacket[byteoffset] 
    for i in range(1,4):
        bytevalue  +=  ackPacket[byteoffset+i] 
    length = int.from_bytes(bytevalue, byteorder='little',signed=False) 
    lengthH = int.from_bytes(ackPacket[35 + 6], byteorder='little',
                             signed=True) 

    #relPosHeading
    byteoffset =24 + 6
    bytevalue = ackPacket[byteoffset] 
    for i in range(1,4):
        bytevalue  +=  ackPacket[byteoffset+i] 
    heading = int.from_bytes(bytevalue, byteorder='little',signed=True) 
    
    return N, E, D, gnssFixOk, carrSoln

def parseLLH(ackPacket):
    
    #PosLon
    byteoffset = 4 + 6
    bytevalue = ackPacket[byteoffset] 
    for i in range(1,4):
        bytevalue  +=  ackPacket[byteoffset+i] 
    Lon = int.from_bytes(bytevalue, byteorder='little',signed=True) 

    #PosLat
    byteoffset =8 + 6
    bytevalue = ackPacket[byteoffset] 
    for i in range(1,4):
        bytevalue  +=  ackPacket[byteoffset+i] 
    Lat = int.from_bytes(bytevalue, byteorder='little',signed=True) 

    #posHeight
    byteoffset =12 + 6
    bytevalue = ackPacket[byteoffset] 
    for i in range(1,4):
        bytevalue  +=  ackPacket[byteoffset+i] 
    Height = int.from_bytes(bytevalue, byteorder='little',signed=True) 

    #Height above mean sea level
    byteoffset =16 + 6
    bytevalue = ackPacket[byteoffset] 
    for i in range(1,4):
        bytevalue  +=  ackPacket[byteoffset+i] 
    hMSL = int.from_bytes(bytevalue, byteorder='little',signed=True) 

    return Lon, Lat, Height, hMSL

class Gnss:
    """
    GNSS Module

    This class is used to interface the GNSS Module
    """ 

    def __init__(self,
                 serial_path="/dev/ttyACM0", 
                 baud=115200, 
                 window_length=3,
                 data_processor=MedianFilter(),
                 log_file=None,
                 max_samples=100000):
        """
        Initialises the GNSS data handler with the default serial path and baud
        rate, sets up storage for the relative North East Down position (in
        meters) of the rover (quadcopter) to the base station, as well as
        latitude, longitude, and altitude, and starts a background thread to
        continuously read and parse GNSS data.

        :param serial_path: Path to the serial port where the GNSS is
                            connected; default: "/dev/ttyACM0"
        :param baud: baud rate of serial communication; defaults to 57600
        :param window_length: length of window of measurements; default: 3
        :param data_processor: data processor on buffer of measurements;
                               default: MedianFilter()
        :param log_file: file name to log data; default: None 
        :param max_samples: maximum number of samples to record; default:
            100000

        If `log_file` is None, the data is not logged; otherwise, on exit, the
        data are stored in a CSV file
        """
        self.__lock = Lock()
        self.__thread = Thread(target=self.__get_measurements_in_background_t,
                               args=[serial_path, baud])
        self.__keep_going = True
        self.__window_length = window_length
        self.__values_cache = np.tile(np.nan, (self.__window_length, 9))
        self.__cursor = 0
        self.__data_processor = data_processor
        self.__log_file = log_file
        self.__max_samples = max_samples
        self.__average_altitude = None
        if log_file is not None:
            feature_names = ("Date_Time", "N", "E", "D", "gnss status", 
                             "rtk status", "Lon", "Lat", "Height", "hMSL")
            self.__logger = DataLogger(num_features=9,
                                       max_samples=max_samples,
                                       feature_names=feature_names)    
        self.__thread.start()
        self.__gnss_altitude_initialisation()

    def __get_measurements_in_background_t(self, serial_path, baud):
        """
        Continuously reads GNSS data from the serial port, parsing UBX message,
        updating the object's GNSS attributes accordingly. 

        :param serial_path: Serial port path
        :param baud: Baud rate for the serial connection
        """

        lenRELPOSNED = 6 + 64 +2
        lenPOSLLH = 6 + 28 + 2
        buffsize = lenRELPOSNED + lenPOSLLH 

        while self.__keep_going:
       
            with serial.Serial(serial_path, baud, timeout=1) as ser:
                readbytes =[] 
                for i in range(buffsize):
                    readbytes.append(ser.read())
            ubxmsg = readUBX(readbytes)

            with self.__lock:
                self.__values_cache[self.__cursor, :] = ubxmsg
                if (self.__log_file is not None 
                        and self.__cursor < self.__max_samples):
                    current_timestamp = datetime.datetime.now()
                    self.__logger.record(current_timestamp, ubxmsg)
                self.__cursor = ((self.__cursor + 1) 
                % self.__window_length)
            if not self.__keep_going:
                    ser.close()
                    return

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.__keep_going = False
        self.__thread.join()  # Wait for the thread to finish
        if self.__log_file is not None:
            self.__logger.save_to_csv(self.__log_file)

    def __gnss_altitude_initialisation(self, num_samples=10):  
        """
        Returns the calibrated GNSS altitude based on the average altitude
        measured in the first minute of readings.
        """
        sum_altitudes = 0  
        i = 0
        while True:            
            current_altitude = self.altitude
            if not np.isnan(current_altitude):
                i += 1
                sum_altitudes += current_altitude
            if i == num_samples:
                break
        average_altitude = sum_altitudes / num_samples
        self.__average_altitude = average_altitude

    @property
    def all_gnss_data(self):
        """
        Returns all GNSS data 

        This method returns all sensor data after the application of the data
        preprocessor specified in the constructor. The data is returned as a
        numpy array with the following data (in this order):
          - Relative North position of quadcopter to base station in meters.
          - Relative East position of quadcopter to base station in meters.
          - Relative Down position of quadcopter to base station in meters.
          - Latitude in decimal 
          - Longitude in decimal 
          - Altitude/Height
          - Height above mean sea level
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, :], 
                                                 cursor=self.__cursor)

    @property
    def relative_north(self):
        """
        The distance of the quadcopter in meters in the north direction
        relative to the base station
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 0], 
                                                 cursor=self.__cursor)

    @property
    def relative_east(self):
        """
        The distance of the quadcopter in meters in the east direction relative
        to the base station
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 1], 
                                                 cursor=self.__cursor)
        
    @property
    def relative_down(self):
        """
        The distance of the quadcopter in meters in the down direction relative
        to the base station
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 2], 
                                                 cursor=self.__cursor)

    @property
    def altitude(self):
        """
        Returns the Altitude of the quadcopter in meters based of the relative
        Down position of the quadcopter compared to the base station.
        """
        with self.__lock:
            current_altitude = - self.__data_processor.process(
                self.__values_cache[:, 2], cursor=self.__cursor)
            # Check if __average_altitude is not None and subtract it from
            # current altitude
            if self.__average_altitude is not None:
                return current_altitude - self.__average_altitude
            else:
                return current_altitude
            
    @property
    def position_latitude(self):
        """
        Returns Latitude position in decimal degrees
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 3], 
                                                 cursor=self.__cursor)

    @property
    def position_longitude(self):
        """
        Returns Longitude position in decimal degrees
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 4], 
                                                 cursor=self.__cursor)
        
    @property
    def position_altitude(self):
        """
        Returns the Altitude position
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 5], 
                                                 cursor=self.__cursor)
        
if __name__ == '__main__':

    while True:
        filename = datetime.datetime.now().strftime("Gnss_%d-%m-%y--%H-%M.csv")
        processor = MedianFilter()
        with Gnss(window_length=5,
                  data_processor=processor,
                  log_file=filename) as gnss_sensor:
            for i in range(10000):
              time.sleep(0.5)
              print(gnss_sensor.altitude)
import serial
import numpy as np
from threading import Thread, Lock
import time
import datetime
from .data_logger import DataLogger
from .filters import MedianFilter


class Gnss:
    """
    GNSS Module

    This class is used to interface the GNSS Module
    """

    #RELPOSNED and PVT
    # Taken from https://github.com/mnltake/readF9P_UBX
    def __readUBX(self, readbytes):
        RELPOSNED = b'\x3c'
        PVT =b'\x07'
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
                    payloadlength = int.from_bytes(ackPacket[4]+ackPacket[5], byteorder='little',signed=False) 
                    i += 1
                elif (i > 5) :
                    ackPacket.append(incoming_byte)
                    i += 1
            if self.__checksum(ackPacket,payloadlength) :
                if ackPacket[3] == RELPOSNED:
                    N, E, D = self.__perseNED(ackPacket)
                elif ackPacket[3] == POSLLH:
                    Lon, Lat, Height, hMSL = self.__perseLLH(ackPacket)
                elif ackPacket[3] == PVT:
                    PVT_Lon, PVT_Lat, PVT_Height = self.__persePVT(ackPacket)
        return N, E, D, Lon, Lat, Height, hMSL, PVT_Lon, PVT_Lat, PVT_Height

    def __checksum(self, ackPacket, payloadlength):
        CK_A =0
        CK_B =0
        for i in range(2, payloadlength+ 6):
            CK_A = CK_A + int.from_bytes(ackPacket[i], byteorder='little',signed=False) 
            CK_B = CK_B +CK_A
        CK_A &=0xff
        CK_B &=0xff
        if (CK_A ==  int.from_bytes(ackPacket[-2], byteorder='little',signed=False)) and (CK_B ==  int.from_bytes(ackPacket[-1], byteorder='little',signed=False)):
            #print("ACK Received")
            return True
        else :
            print("ACK Checksum Failure:")  
            return False

    def __perseNED(self, ackPacket):
        #relPosN
        byteoffset =8 + 6
        bytevalue =  ackPacket[byteoffset] 
        for i in range(1,4):
            bytevalue  +=  ackPacket[byteoffset+i] 
        N = int.from_bytes(bytevalue, byteorder='little',signed=True) 
        NH = int.from_bytes(ackPacket[32 + 6], byteorder='little',signed=True) 

        #relPosE
        byteoffset =12 + 6
        bytevalue = ackPacket[byteoffset] 
        for i in range(1,4):
            bytevalue  +=  ackPacket[byteoffset+i] 
        E = int.from_bytes(bytevalue, byteorder='little',signed=True) 
        EH = int.from_bytes(ackPacket[33 + 6], byteorder='little',signed=True) 

        #relPosD
        byteoffset =16 + 6
        bytevalue = ackPacket[byteoffset] 
        for i in range(1,4):
            bytevalue  +=  ackPacket[byteoffset+i] 
        D = int.from_bytes(bytevalue, byteorder='little',signed=True) 
        DH = int.from_bytes(ackPacket[34 + 6], byteorder='little',signed=True)     #print("D:%0.2f cm" %posned["D"]  )

        #Carrier solution status
        flags = int.from_bytes(ackPacket[60 + 6], byteorder='little',signed=True) 
        gnssFixOk =  flags  & (1 << 0) #gnssFixOK 
        carrSoln =  (flags   & (0b11 <<3)) >> 3 #carrSoln0:no carrier 1:float 2:fix

        #GPS time
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
        lengthH = int.from_bytes(ackPacket[35 + 6], byteorder='little',signed=True) 

        #relPosHeading
        byteoffset =24 + 6
        bytevalue = ackPacket[byteoffset] 
        for i in range(1,4):
            bytevalue  +=  ackPacket[byteoffset+i] 
        heading = int.from_bytes(bytevalue, byteorder='little',signed=True) 
        
        return N, E, D, gnssFixOk, carrSoln

    def __perseLLH(self, ackPacket):
        
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

    def __persePVT(self, ackPacket):
        #PosLon
        byteoffset = 24 + 6
        bytevalue = ackPacket[byteoffset] 
        for i in range(1,4):
            bytevalue  +=  ackPacket[byteoffset+i] 
        Lon = int.from_bytes(bytevalue, byteorder='little',signed=True) 
    
        #PosLat
        byteoffset =28 + 6
        bytevalue = ackPacket[byteoffset] 
        for i in range(1,4):
            bytevalue  +=  ackPacket[byteoffset+i] 
        Lat = int.from_bytes(bytevalue, byteorder='little',signed=True) 

        #posHeight
        byteoffset =32 + 6
        bytevalue = ackPacket[byteoffset] 
        for i in range(1,4):
            bytevalue  +=  ackPacket[byteoffset+i] 
        Height = int.from_bytes(bytevalue, byteorder='little',signed=True) 

        #Height above mean sea level
        byteoffset =36 + 6
        bytevalue = ackPacket[byteoffset] 
        for i in range(1,4):
            bytevalue  +=  ackPacket[byteoffset+i] 
        hMSL = int.from_bytes(bytevalue, byteorder='little',signed=True) 

        #Ground Speed
        byteoffset =60 + 6
        bytevalue = ackPacket[byteoffset] 
        for i in range(1,4):
            bytevalue  +=  ackPacket[byteoffset+i] 
        gSpeed = int.from_bytes(bytevalue, byteorder='little',signed=True) 

        #Heading of motion
        byteoffset =64 + 6
        bytevalue = ackPacket[byteoffset] 
        for i in range(1,4):
            bytevalue  +=  ackPacket[byteoffset+i] 
        headMot = int.from_bytes(bytevalue, byteorder='little',signed=True) 

        return Lon, Lat, Height

    def __init__(self, 
                 parse_nmea=False,
                 serial_path="/dev/ttyACM0", 
                 baud=57600, 
                 window_length=3,
                 data_processor=MedianFilter(),
                 log_file=None,
                 max_samples=100000):
        """
        Initialises the GPS data handler with the default serial path and baud
        rate, sets up storage for latitude, longitude, and altitude, and starts
        a background thread to continuously read and parse GPS data.

        :param serial_path: Path to the serial port where the GPS is connected;
                            default: "/dev/ttyACM0"
        :param baud: baud rate of serial communication; defaults to 57600
        :param window_length: length of window of measurements; default: 3
        :param data_processor: data processor on buffer of measurements; 
                               default: MedianFilter()
        :param log_file: file name to log data; default: None 
        :param max_samples: maximum number of samples to record; 
                            default: 100000

        If `log_file` is None, the data is not logged; otherwise, on exit, 
        the data are stored in a CSV file

        Note: We assume that we receive 3 measurements from the anemometer
        """
        self.__lock = Lock()
        self.__thread = Thread(target=self.__get_measurements_in_background_t,
                               args=[serial_path, baud])
        self.__keep_going = True
        self.__window_length = window_length
        self.__values_cache = np.tile(np.nan, (self.__window_length, 10))
        self.__cursor = 0
        self.__data_processor = data_processor
        self.__log_file = log_file
        self.__max_samples = max_samples
        if log_file is not None:
            feature_names = ("Date_Time", "N", "E", "D", "Lon", "Lat", "Height", "hMSL", "PVT_Lon", "PVT_Lat", "PVT_Height")
            self.__logger = DataLogger(num_features=10,
                                       max_samples=max_samples,
                                       feature_names=feature_names)    
        self.__thread.start()

    def __get_measurements_in_background_t(self, serial_path, baud):
        """
        Continuously reads GPS data from the serial port, parsing GNGLL
        messages for latitude and longitude, and GPGSV messages for altitude,
        updating the object's GPS attributes accordingly. 

        :param serial_path: Serial port path
        :param baud: Baud rate for the serial connection
        """

        lenRELPOSNED = 6 + 64 +2
        lenPOSLLH = 6 + 28 + 2
        lenPVT = 6 + 92 +2
        buffsize = lenRELPOSNED + lenPVT + lenPOSLLH 

        while self.__keep_going:
       
            with serial.Serial(serial_path, baud, timeout=1) as ser:
                readbytes =[] 
                for i in range(buffsize):
                    readbytes.append(ser.read())
            ubxmsg = self.__readUBX(readbytes)
            print(ubxmsg)

            with self.__lock:
                self.__values_cache[self.__cursor, :] = ubxmsg
                if (self.__log_file is not None 
                        and self.__cursor < self.__max_samples):
                    data_to_log = self.__data_processor.process(
                        self.__values_cache[:, :], 
                        cursor=self.__cursor)
                    # Process the data only if it doesn't contain NaN
                    # values
                    if not np.isnan(data_to_log).any():
                            current_timestamp = datetime.datetime.now()
                            self.__logger.record(current_timestamp, 
                                                    data_to_log)
                self.__cursor = ((self.__cursor + 1) 
                % self.__window_length)

        ser.close()
        return

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.__keep_going = False
        self.__thread.join()  # Wait for the thread to finish
        if self.__log_file is not None:
            self.__logger.save_to_csv(self.__log_file)

    @property
    def all_gnss_data(self):
        """
        Returns all GNSS data 

        This method returns all sensor data after the application of the data
        preprocessor specified in the constructor. The data is returned as a
        numpy array with the following data (in this order):
          - Latitude in decimal 
          - Longitude in decimal 
          - Altitude
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, :], 
                                                 cursor=self.__cursor)

    @property
    def Latitude(self):
        """
        Returns Latitude position in decimal
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 0], 
                                                 cursor=self.__cursor)

    @property
    def Longitude(self):
        """
        Returns Longitude position in decimal
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 1], 
                                                 cursor=self.__cursor)

    @property
    def Altitude(self):
        """
        Returns the Altitude position
        """
        with self.__lock:
            return self.__data_processor.process(self.__values_cache[:, 2], 
                                                 cursor=self.__cursor)
        
if __name__ == '__main__':

    while True:
        filename = datetime.datetime.now().strftime("Gnss_%d-%m-%y--%H-%M.csv")
        processor = MedianFilter()
        with Gnss(window_length=5,
                  data_processor=processor,
                  log_file=filename) as gnss_sensor:
            time.sleep(600) # set time for how long you want to record data 
                            # for in seconds

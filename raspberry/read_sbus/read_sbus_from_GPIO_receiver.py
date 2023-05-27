import read_sbus_from_GPIO
import time
import serial
from radioDataParser import RadioDataParser

SBUS_PIN = 25 #pin where sbus wire is plugged in
ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1) #serial connection between Pi and ESP32
ser.reset_input_buffer()                               #serial.Serial(port, buad rate, timeout)

reader = read_sbus_from_GPIO.SbusReader(SBUS_PIN)
reader.begin_listen()

#wait until connection is established
while(not reader.is_connected()):
    time.sleep(.2)

#Note that there will be nonsense data for the first 10ms or so of connection
#until the first packet comes in.
time.sleep(.1)

parser = RadioDataParser()

while True:
        try:
                is_connected = reader.is_connected()
                packet_age = reader.get_latest_packet_age() #milliseconds

                #returns list of length 16, so -1 from channel num to get index
                channel_data = reader.translate_latest_packet()
                # check if data is in range [1000, 2000]
                parser.m_channelData = map(lambda x: 0 if int(x) < 0 else (2000 if int(x) > 2000 else int(x)), channel_data.strip().split(","))
                # process and encapsulate the data
                # the output data packet format will be as follows
                # Y_radPs, P_rad, R_rad, T_PWM_MIN2MAX, % trimA, % trimB, % trimC, % trimE, encodedSwitchesData
                # here the final data value encodedSwitchesData is an integer carrying information 
                # of the position of switches A, B, C, and D in the last 5-bits (the rightmost 5-bits),
                # in which each bit corresponds to data as follows
                # bit-4 (MSB): 1-bit info of Switch B: 1 if armed else 0
                # bit-3: 1-bit info of Switch A: 1 if kill_on else 0
                # bits 2 and 1: 2-bit info of switch C: 00 for position DOWN, 01 for position MID, 10 for position UP
                # bit-0: 1-bit info of switch D: 1 if D_on else 0
                channel_data = parser.encapsulateRadioData()
                #print(channel_data) #Uncomment to Print data received on Pi from the RC receiver

                # Send with S in the beginning to indicate the start of the data, and also useful to check if data 
                # is received properly on the ESP's end
                ser.write(f'S,{channel_data}\n'.encode()) #Send data from Pi to ESP32
                # ser.write(b"\n") #Starts a new line so ESP32 knows when to stop reading
                
                while ser.inWaiting() > 0:
                        try:
                                line = ser.readline().  decode('ascii').rstrip()
                                #print(line)
                        except UnicodeDecodeError as e:
                                print(f"UnicodeDecodeError {e}, retrying....")
                else:
                        pass
                        #print("no data")

                time.sleep(0.01)
                
        except KeyboardInterrupt:
                #cleanup cleanly after ctrl-c
                reader.end_listen()
                exit()
        except:
                #cleanup cleanly after error
                reader.end_listen()
                raise



    


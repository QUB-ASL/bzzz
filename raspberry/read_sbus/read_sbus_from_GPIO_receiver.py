import read_sbus_from_GPIO
import time
import serial

SBUS_PIN = 25 #pin where sbus wire is plugged in
ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
ser.reset_input_buffer()

reader = read_sbus_from_GPIO.SbusReader(SBUS_PIN)
reader.begin_listen()

#wait until connection is established
while(not reader.is_connected()):
    time.sleep(.2)

#Note that there will be nonsense data for the first 10ms or so of connection
#until the first packet comes in.
time.sleep(.1)

while True:
        try:
                is_connected = reader.is_connected()
                packet_age = reader.get_latest_packet_age() #milliseconds

                #returns list of length 16, so -1 from channel num to get index
                channel_data = reader.translate_latest_packet()
                #print(channel_data)

                #
                #Do something with data here!
                #ex:print(f'{channel_data[0]}')
                #

                
                ser.write(f'{channel_data}'.encode())
                ser.write(b"\n")
                
                while ser.inWaiting() > 0:
                        try:
                                line = ser.readline().  decode('ascii').rstrip()
                                print(line)
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



    


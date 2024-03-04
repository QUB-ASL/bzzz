import read_sbus_from_GPIO
import time

SBUS_PIN = 25  # pin where sbus wire is plugged in

reader = read_sbus_from_GPIO.SbusReader(SBUS_PIN)
reader.begin_listen()

# wait until connection is established
while (not reader.is_connected()):
        time.sleep(.2)

# Note that there will be nonsense data for the first 10ms or so of connection
# until the first packet comes in.
time.sleep(.1)

while True:
        try:
                is_connected = reader.is_connected()
                packet_age = reader.get_latest_packet_age()  # milliseconds

                # returns list of length 16, 
                # so take away 1 from channel num to get index
                channel_data = reader.translate_latest_packet()

                print(channel_data) #Prints 16 channels of data from receiver

        except KeyboardInterrupt:
                # cleanup cleanly after ctrl-c
                reader.end_listen()
                exit()
        except:
                # cleanup cleanly after error
                reader.end_listen()
                raise
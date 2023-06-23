import read_sbus_from_GPIO
import time
import serial
from radioDataParser import RadioDataParser


SBUS_PIN = 25  # pin where sbus wire is plugged in
# serial connection between Pi and ESP32
ser = serial.Serial('/dev/ttyUSB0', 500000, timeout=1)
ser.reset_input_buffer()

reader = read_sbus_from_GPIO.SbusReader(SBUS_PIN)
reader.begin_listen()

# wait until connection is established
while (not reader.is_connected()):
    time.sleep(.2)

# Note that there will be nonsense data for the first 10ms or so of connection
# until the first packet comes in.
time.sleep(.1)

parser = RadioDataParser()

def get_radio_data():
    is_connected = reader.is_connected()
    packet_age = reader.get_latest_packet_age()  # milliseconds

    # returns list of length 16, so -1 from channel num to get index
    channel_data = str(reader.translate_latest_packet())[1:-1]

    return is_connected, packet_age, channel_data


def parse_radio_data(channel_data):
    # check if data is in range [1000, 2000]
    parser.m_channelData = list(map(lambda x: 0 if int(x) < 0 else (
        2000 if int(x) > 2000 else int(x)), channel_data.strip().split(",")))
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
    channel_data = parser.format_radio_data_for_sending()
    return channel_data


def send_data_to_ESP(channel_data):
    # Send with S in the beginning to indicate the start of the data, and also useful to check if data
    # is received properly on the ESP's end
    # Send data from Pi to ESP32, send a new line char so ESP32 knows when to stop reading
    ser.write(f'S,{channel_data}\n'.encode())


def receive_data_from_ESP():
    """Read data from ESP32 via UART.

    :return: String if data is received, None otherwise.
    """
    while ser.inWaiting() > 0:
        try:
            line = ser.readline().decode('ascii').rstrip()
            return line
        except UnicodeDecodeError as e:
            print(f"UnicodeDecodeError {e}, retrying....")
    else:
        return None


def print_receive_data_from_ESP():
    """Read data from ESP32 via UART and print iff data is received.
    """
    received_data = receive_data_from_ESP()
    if received_data is not None:
        print(received_data)


def get_radio_data_parse_and_send_to_ESP(return_channel_date = False):
    """Read the radio data, process it, format it into a string, and send it via UART.
    """
    try:
        _is_connected, _packet_age, channel_data = get_radio_data()
        if _is_connected:
            channel_data = parse_radio_data(channel_data)
            send_data_to_ESP(channel_data)
            if return_channel_date: 
                return channel_data
    except KeyboardInterrupt:
        # cleanup cleanly after ctrl-c
        reader.end_listen()
        exit()
    except:
        # cleanup cleanly after error
        reader.end_listen()
        raise


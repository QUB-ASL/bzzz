import read_sbus_from_GPIO
import time
import serial
from radioDataParser import RadioDataParser
import threading


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

# TODO: implement the below loop as a thread with frequency 50Hz.
#       Might want to .join() and manage threads using
#       ThreadPoolExecutor as a context manager for multi-threading tasks
#       such as altitude hold, loitering algos for future usage.
# NOTE: When a thread terminates with an exception, the ThreadPoolExecutor
#       will not report it, so might want to handel exceptions properly
#       in the threaded functions
# NOTE: The order of execution of pooled threads cannot be predicted, this is
#       highly dependent on what the OS does at that time.
#       This will cause many synchronization issues and racing conditions if
#       they use shared resources, for example let us say that thread_1 needs
#       results of thread_2, so the required order of execution is start thread_2,
#       let it finish, start thread_1, let it finish.
#       But pooling threads 1 and 2 cannot gurantee which of the two run first.
#       It beocmes worse if they share resources, as one might not be aware that the
#       other changed some values in the shared resurce (not thread-safe).
#       Possible solution is to use Locks (but make sure to release them).


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


def get_radio_data_parse_and_send_to_ESP():
    """Read the radio data, process it, format it into a string, and send it via UART.
    """
    try:
        _is_connected, _packet_age, channel_data = get_radio_data()
        channel_data = parse_radio_data(channel_data)
        send_data_to_ESP(channel_data)
    except KeyboardInterrupt:
        # cleanup cleanly after ctrl-c
        reader.end_listen()
        exit()
    except:
        # cleanup cleanly after error
        reader.end_listen()
        raise


def run_thread_every_given_interval(interval,
                                    function_to_run,
                                    num_times_to_run=0):
    """
    Create a thread of the given function, attach a timer 
    to it and run it everytime the interval is elapsed.

    :param interval: Interval between each run in seconds. 
        Note: the given interval must be larger than worst 
        execution time of the given function.
    :param function_to_run: Function handle which is to be run.
    :param num_times_to_run: Number of times to run the thread before killing it
        0 means that the thread is called as long as the program doesn't 
        terminate, defaults to 0.
    """
    if num_times_to_run != 1:
        threading.Timer(interval, run_thread_every_given_interval, [
                        interval, function_to_run, num_times_to_run if num_times_to_run else 0]).start()
    function_to_run()


# Run the get_radio_data_parse_and_send_to_ESP funtionn @ 50Hz
run_thread_every_given_interval(0.02, get_radio_data_parse_and_send_to_ESP)

import bzzz.read_sbus.read_sbus_from_GPIO
import time

import bzzz.read_sbus.radioData

class RC:
    """
    This class is used to interface the remote control (receiver) with the Raspberry Pi.
    """

    def __init__(self,
                 serial_path='/dev/ttyUSB0',
                 baud=500000,
                 sbus_pin = 25):
        """
        Create a new instance of RC

        :param serial_path: serial path; defaults to /dev/ttyUSB0 on RPi
        :param baud: baud rate of serial communication; defaults to 500000
        :param sbus_pin: RPi GPIO pin where RC receiver sbus wire is plugged in
        """

        self.reader = bzzz.read_sbus.read_sbus_from_GPIO.SbusReader(sbus_pin)
        self.reader.begin_listen()

        # wait until connection is established
        still_waiting = False
        while (not self.reader.is_connected()):
            print("{still_waiting_text}aiting for radio connection to establish....".format(
                still_waiting_text="Still w" if still_waiting else "W"))
            time.sleep(.2)
            still_waiting = True

        # Note that there will be nonsense data for the first 10ms or so of connection
        # until the first packet comes in.
        time.sleep(.1)
        self.parser = bzzz.read_sbus.radioData.RadioData()
        self.__parsed_data = None

    def get_radio_data(self,
                       max_packet_age_in_ms=500):
        """
        Checks if the radio is connected, determines when the last RC data was
        received and reads the 16 channels of data received from the RC

        :param max_packet_age_in_ms: max age a packet can be im ms. Therefore 
        how long the quadcopter can fly since it last read the receiver.
        defualt 500ms

        Returns: tuple (connection_lost_flag, channel_data)
        """
        is_connected = self.reader.is_connected()
        packet_age = self.reader.get_latest_packet_age()  # milliseconds
        connection_lost = packet_age > max_packet_age_in_ms \
            or not is_connected

        channel_data = None
        # returns list of length 16, so -1 from channel num to get index
        if not connection_lost:
            channel_data = str(self.reader.translate_latest_packet())[1:-1]

        return connection_lost, channel_data

    def parse_radio_data(self, 
                         channel_data,
                         over_write_throttle_ref_to=-1):
        """
        This function checks that the channel data from the remote is in the correct range and then formates it correctly to be sent to the ESP32.
        
        :param channel_data: The channel data from the remote that we want to check is in the correct range
        :param over_write_throttle_ref_to: When altitude hold is active we want to overwrite the throttle reference from the remote. 
               This sends the new throttle value, if set to -1 the reference throttle is kept; default: -1.
        """
        # check if data is in range [1000, 2000]
        self.parser.m_channelData = list(map(lambda x: 0 if int(x) < 0 else (
            2000 if int(x) > 2000 else int(x)), channel_data.strip().split(",")))

        if over_write_throttle_ref_to != -1:
            # TODO: check if channel 2 is throttle data
            self.parser.m_channelData[2] = over_write_throttle_ref_to
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
        self.__parsed_data, channel_data = self.parser.format_radio_data_for_sending()
        return channel_data

    def send_data_to_ESP(self, channel_data):
        # Send with S in the beginning to indicate the start of the data, and also useful to check if data
        # is received properly on the ESP's end
        # Send data from Pi to ESP32, send a new line char so ESP32 knows when to stop reading
        self.ser.write(f'S,{channel_data}\n'.encode())

    def receive_data_from_ESP(self):
        """
        Read data from ESP32 via UART.

        :return: String if data is received, None otherwise.
        """
        while self.ser.inWaiting() > 0:
            try:
                line = self.ser.readline().decode('ascii').rstrip()
                return line
            except UnicodeDecodeError as e:
                print(f"UnicodeDecodeError {e}, retrying....")
        else:
            return None

    def __get_radio_data_parse_and_send_to_ESP(self,
                                             return_channel_data=False,
                                             force_send_fake_data=False,
                                             fake_data="",
                                             over_write_throttle_ref_to=-1):
        """
        Read the radio data, process it, format it into a string, and send it via UART.

        :param return_channel_data: 
        :param force_send_fake_data: whether or not to send fake data; default: False.
        :param fake_data: if force_send_fake_data = True, this is that data that is to be sent, it should start with "S"; default: "".
        :param over_write_throttle_ref_to: When altitude hold is active we want to overwrite the throttle reference from the remote. 
               This sends the new throttle value, if set to -1 the reference throttle is kept; default: -1.
        """
        try:
            connection_lost, channel_data = self.get_radio_data()
            channel_data = self.parse_radio_data(
                channel_data, over_write_throttle_ref_to=over_write_throttle_ref_to)
            if force_send_fake_data:
                channel_data = fake_data
            self.send_data_to_ESP(channel_data)
            if return_channel_data:
                return channel_data
        except KeyboardInterrupt:
            # cleanup cleanly after ctrl-c
            self.reader.end_listen()
            exit()
        except:
            # cleanup cleanly after error
            self.reader.end_listen()
            raise

    def yaw_rate_reference_rad_sec(self) -> float:
        return self.__parsed_data[0]

    def pitch_reference_angle_rad(self) -> float:
        return self.__parsed_data[1]

    def roll_reference_angle_rad(self) -> float:
        return self.__parsed_data[2]

    def throttle_reference_percentage(self) -> float:
        return self.__parsed_data[3]

    def trimmer_VRA_percentage(self):
        return self.__parsed_data[4]

    def trimmer_VRB_percentage(self):
        return self.__parsed_data[5]

    def trimmer_VRC_percentage(self):
        return self.__parsed_data[6]

    def trimmer_VRE_percentage(self):
        return self.__parsed_data[7]

    def switch_B(self):
        return (self.__parsed_data[8] & 0x10) >> 4

    def switch_A(self):
        return (self.__parsed_data[8] & 0x08) >> 3

    def switch_C(self):
        return (self.__parsed_data[8] & 0x06) >> 1

    def switch_D(self):
        return self.__parsed_data[8] & 0x01
    

if __name__ == '__main__':
    rc = RC()
    while True:
        rc.get_radio_data()
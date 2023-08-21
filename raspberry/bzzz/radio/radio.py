from bzzz.radio.radio_data_receiver import RadioDataReceiver
from bzzz.radio.radio_data_parser import RadioDataParser
from bzzz.radio.radio_data_sender import RadioDataSender

class Radio:
    def __init__(self):
        self.__receiver = RadioDataReceiver()
        self.__parser = RadioDataParser()
        self.__sender = RadioDataSender()

        self.__parsed_data = None

    def parse_radio_data(self, channel_data, over_write_throttle_ref_to=-1):
        # check if data is in range [1000, 2000]
        self.__parser.m_channelData = list(map(lambda x: 0 if int(x) < 0 else (
            2000 if int(x) > 2000 else int(x)), channel_data))

        if over_write_throttle_ref_to != -1:
            self.__parser.m_channelData[2] = over_write_throttle_ref_to
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
        self.__parsed_data, channel_data = self.__parser.format_radio_data_for_sending()
        return channel_data

    def receive_parse_and_send( self,
                                return_channel_date=False,
                                force_send_fake_data=False,
                                fake_data="",
                                over_write_throttle_ref_to=-1,
                                perform_RC_check=False):
        """Read the radio data, process it, format it into a string, and send it via UART.
        """
        try:
            # Receive Radio data
            _is_connected, _packet_age, channel_data = self.__receiver.get_radio_data()

            # Parse Radio data
            if not _is_connected:
                print(
                    f"Radio not connected; Status _is_connected: {_is_connected}")
            else:
                channel_data = self.parse_radio_data(
                    channel_data, over_write_throttle_ref_to=over_write_throttle_ref_to)
                if force_send_fake_data:
                    channel_data = fake_data

                # Do RC check
                RC_check_status = False
                if perform_RC_check:
                    if self.throttle_reference_percentage() > 0.05:
                        print(f"Please zero the throttle. Current throttle is {self.throttle_reference_percentage()}")
                    elif not self.switch_A():
                        print(f"Please disable switch A. Current status of switch A is {self.switch_A()}")
                    elif not self.switch_B():
                        print(f"Please disable switch B. Current status of switch B is {self.switch_B()}")
                    elif not self.switch_C():
                        print(f"Please disable switch C. Current status of switch C is {self.switch_C()}")
                    elif self.switch_D():
                        print(f"Please Enable switch D. Current status of switch D is {self.switch_D()}")
                    else:
                        RC_check_status = True
                    return RC_check_status
                else:
                    RC_check_status = True

                # Send Radio data
                if RC_check_status:
                    self.__sender.send_data_to_ESP(channel_data)
            if return_channel_date:
                return channel_data
        except KeyboardInterrupt:
            # cleanup cleanly after ctrl-c
            self.__receiver.reader.end_listen()
            exit()
        except:
            # cleanup cleanly after error
            self.__receiver.reader.end_listen()
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

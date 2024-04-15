import bzzz.read_sbus.read_sbus_from_GPIO
import time

import bzzz.read_sbus.radioData


class RC:
    """
    Radio receiver interface
    """

    def __init__(self,
                 sbus_pin=25):
        """
        Create a new instance of RC

        :param sbus_pin: RPi GPIO pin where RC receiver sbus wire is plugged in
        """
        self.__reader = bzzz.read_sbus.read_sbus_from_GPIO.SbusReader(sbus_pin)
        self.__reader.begin_listen()
        # wait until connection is established
        while (not self.__reader.is_connected()):
            print("Waiting for radio connection to establish...")
            time.sleep(.2)

        # Note that there will be nonsense data for the first 10ms or so of
        # connection until the first packet comes in.
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
        is_connected = self.__reader.is_connected()
        packet_age = self.__reader.get_latest_packet_age()  # milliseconds
        connection_lost = packet_age > max_packet_age_in_ms \
            or not is_connected

        channel_data = str(self.__reader.translate_latest_packet())[1:-1]

        return connection_lost, channel_data

    def yaw_rate_reference_rad_sec(self) -> float:
        return self.__parsed_data[0]

    def pitch_reference_angle_rad(self):
        return self.__parsed_data[1]

    def roll_reference_angle_rad(self):
        return self.__parsed_data[2]

    def throttle_reference_percentage(self):
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
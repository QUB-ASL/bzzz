import bzzz.radio.read_sbus_from_GPIO
import time
import bzzz.radio.radio_data_parser
import threading


class RadioDataReceiver:
    SBUS_PIN = 25  # pin where sbus wire is plugged in

    def __init__(self):
        self.reader = bzzz.radio.read_sbus_from_GPIO.SbusReader(
            RadioDataReceiver.SBUS_PIN)
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

    def get_radio_data(self):
        is_connected = self.reader.is_connected()
        packet_age = self.reader.get_latest_packet_age()  # milliseconds

        # returns list of length 16, so -1 from channel num to get index
        channel_data_list = self.reader.translate_latest_packet()

        return is_connected, packet_age, channel_data_list

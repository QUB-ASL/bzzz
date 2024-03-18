import serial


class EspBridge:
    """
    Interface between Raspberry Pi and ESP32
    """

    def __init__(self,
                 serial_path='/dev/ttyUSB0',
                 baud=500000):
        self.ser = serial.Serial(serial_path, baud, timeout=1)
        self.ser.reset_input_buffer()

    def send_to_esp(self, radio_data):
        """
        Send data to ESP32

        :param radio_data: instance of RadioData
        """
        data_to_go = radio_data.format_radio_data_for_sending()
        data_to_ser = f'S,{data_to_go}\n'.encode()
        self.ser.write(data_to_ser)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self.ser is not None:
            self.ser.close()

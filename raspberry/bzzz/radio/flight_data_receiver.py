from ESP_interface import ESPInterface

class FlightDataReceiver:
    def __init__(self):
        self.ser = ESPInterface.SER
    
    def receive_data_from_ESP(self):
        """Read data from ESP32 via UART.

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
from ESP_interface import ESPInterface

class RadioDataSender:
    def __init__(self):
        self.ser = ESPInterface.SER

    def send_data_to_ESP(self, channel_data):
        # Send with S in the beginning to indicate the start of the data, and also useful to check if data
        # is received properly on the ESP's end
        # Send data from Pi to ESP32, send a new line char so ESP32 knows when to stop reading
        self.ser.write(f'S,{channel_data}\n'.encode())
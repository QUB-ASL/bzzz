import serial

class EspBridge:

    def __init__(self,
                 serial_path='/dev/ttyUSB0',
                 baud=500000):
         # serial connection between Pi and ESP32
        self.ser = serial.Serial(serial_path, baud, timeout=1)
        self.ser.reset_input_buffer()
    
    def send_to_esp(self, radio_data):
        # Send with S in the beginning to indicate the start of the data, and also useful to check if data
        # is received properly on the ESP's end
        # Send data from Pi to ESP32, send a new line char so ESP32 knows when to stop reading
        _, data_to_go = radio_data.format_radio_data_for_sending()
        data_to_ser = f'S,{data_to_go}\n'.encode()
        self.ser.write(data_to_ser)
    
    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self.ser is not None:
            self.ser.close()
        

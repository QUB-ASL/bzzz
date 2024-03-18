import serial

class EspBridge:

    def __init__(self,
                 serial_path='/dev/ttyUSB0',
                 baud=500000):
         # serial connection between Pi and ESP32
        self.ser = serial.Serial(serial_path, baud, timeout=1)
        self.ser.reset_input_buffer()
    
    def send_to_esp(self, channel_data):
        # Send with S in the beginning to indicate the start of the data, and also useful to check if data
        # is received properly on the ESP's end
        # Send data from Pi to ESP32, send a new line char so ESP32 knows when to stop reading
        self.ser.write(f'S,{channel_data}\n'.encode())
    
    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self.ser is not None:
            self.ser.close()
        

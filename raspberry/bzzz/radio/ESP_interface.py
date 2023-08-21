import serial

class ESPInterface:
    # serial connection between Pi and ESP32
    SER = serial.Serial('/dev/ttyUSB0', 500000, timeout=1)
    SER.reset_input_buffer()
    
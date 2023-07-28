import serial

ser = serial.Serial('/dev/serial0', 115200, timeout=0.050)

while ser.in_waiting >0:
        data_in = ser.readline()
        print (data_in)

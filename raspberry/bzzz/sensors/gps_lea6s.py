import serial


serial_path = "/dev/tty.usbmodem14301"
baud = 500000
ser = serial.Serial(serial_path, baud, timeout=1)
ser.reset_input_buffer()
while True:
    if ser.in_waiting > 0:
        sensor_data = ser.readline().decode('utf-8').strip()
        # print(sensor_data)
        if sensor_data.startswith("$GPGLL"):
            tokens = sensor_data.split(",")
            print(f"{float(tokens[1])/100}, {float(tokens[3])/100}")
            # print(
            # f"# (MSG {tokens[2]}) <{tokens[4]}> Satellites up there: {tokens[3]}; elevation: {tokens[5]}; azimuth: {tokens[6]} [[{tokens[7]}]]")

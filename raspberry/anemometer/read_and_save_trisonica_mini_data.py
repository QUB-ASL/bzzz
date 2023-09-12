#!/usr/bin/env python3
import serial
import numpy as np
from datetime import datetime
import csv

index = 0
filename = datetime.now().strftime("%d-%m-%y--%H:%M.csv")

with open(filename, "w", newline="") as f:
    # creating the writer
    writer = csv.writer(f)
    # using writerow to write individual record one by one
    writer.writerow(["index","date_time","wind_speed", "wind_speed_2D", "H_direction", "V_direction"])
    f.close()

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
    ser.reset_input_buffer()

    while True:
        if ser.in_waiting > 0:

            line = ser.readline().decode('utf-8').rstrip()
            # print(line)

            index = index + 1

            # Getting the current date and time
            dt = datetime.now()

            all_data = line.split()

            wind_speed = float(all_data[0])
            wind_speed_2D = float(all_data[1])
            H_direction = float(all_data[2])
            V_direction = float(all_data[3])

            with open(filename, "a+", newline="") as f:
                # creating the writer
                writer = csv.writer(f)
                # using writerow to write individual record one by one
                writer.writerow([index, dt, wind_speed, wind_speed_2D, H_direction, V_direction])
                f.close()
            
            # print("Date and time is:", dt)
            # print(all_data)
            # print(wind_speed)
            # print(wind_speed_2D)
            # print(H_direction)
            # print(V_direction)
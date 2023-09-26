#!/usr/bin/env python3
import serial
import numpy as np
import datetime
import csv

index = 0
index_2 = datetime.datetime.now()
index_2 = index_2.replace(second=0, microsecond=0)

filename = datetime.datetime.now().strftime("%d-%m-%y--%H:%M.csv")

with open(filename, "w", newline="") as f:
    # creating the writer
    writer = csv.writer(f)
    # using writerow to write individual record one by one
    writer.writerow(["Index", "Index_2", "Date_Time", "Wind_Speed", "Wind_Speed_2D", "H_direction", "V_direction", "U_axis", "V_axis", "W_axis"])
    f.close()

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
    ser.reset_input_buffer()

    while True:
        if ser.in_waiting > 0:

            line = ser.readline().decode('utf-8').rstrip()
            # print(line)

            index = index + 1
            index_2 = index_2 + datetime.timedelta(microseconds=25000)

            # Getting the current date and time
            dt = datetime.datetime.now()

            all_data = line.split()

            wind_speed = float(all_data[0])
            wind_speed_2D = float(all_data[1])
            H_direction = float(all_data[2])
            V_direction = float(all_data[3])
            U_axis = float(all_data[4])
            V_axis = float(all_data[5])
            W_axis = float(all_data[6])

            with open(filename, "a+", newline="") as f:
                # creating the writer
                writer = csv.writer(f)
                # using writerow to write individual record one by one
                writer.writerow([index, index_2, dt, wind_speed, wind_speed_2D, H_direction, V_direction, U_axis, V_axis, W_axis])
                f.close()
            
            # print("Date and time is:", dt)
            # print(all_data)
            # print(wind_speed)
            # print(wind_speed_2D)
            # print(H_direction)
            # print(V_direction)
            # print(U_axis)
            # print(V_axis)
            # print(W_axis)
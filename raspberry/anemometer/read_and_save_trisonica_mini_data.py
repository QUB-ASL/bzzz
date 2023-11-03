#!/usr/bin/env python3
import serial
import numpy as np
import datetime
import csv

index_array = []
index_2_array = []
dt_array = []
wind_speed = []
wind_speed_2D = []
H_direction =[]
V_direction = []
U_axis = []
V_axis = []
W_axis = []

index = 0
index_2 = datetime.datetime.now()
index_2 = index_2.replace(second=0, microsecond=0)
start_time = datetime.datetime.now()
start_time = start_time.replace(second=0, microsecond=0)

filename = datetime.datetime.now().strftime("%d-%m-%y--%H-%M.csv")

with open(filename, "w", newline="") as f:
    # creating the writer
    writer = csv.writer(f)
    # using writerow to write individual record one by one
    writer.writerow(["Index", "Index_2", "Date_Time", "Wind_Speed", "Wind_Speed_2D", "H_direction", "V_direction", "U_axis", "V_axis", "W_axis"])

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
    ser.reset_input_buffer()

    while True:
        if ser.in_waiting > 0:

            line = ser.readline().decode('utf-8').rstrip()

            index = index + 1
            index_2 = index_2 + datetime.timedelta(microseconds=25000)

            # Getting the current date and time
            dt = datetime.datetime.now()

            all_data = line.split()
            
            index_array.append(index)
            index_2_array.append(index_2)
            dt_array.append(dt)
            wind_speed.append(float(all_data[0]))
            wind_speed_2D.append(float(all_data[1]))
            H_direction.append(float(all_data[2]))
            V_direction.append(float(all_data[3]))
            U_axis.append(float(all_data[4]))
            V_axis.append(float(all_data[5]))
            W_axis.append(float(all_data[6]))

            # Saving All data after set time has passed
            if index_2 == (start_time + datetime.timedelta(minutes = 10)):
                
                with open(filename, "a+", newline="") as f:
                    # creating the writer
                    writer = csv.writer(f)
                    # using writerow to write individual record one by one
                    data_to_save = [index_array, index_2_array, dt_array, wind_speed, wind_speed_2D, H_direction, V_direction, U_axis, V_axis, W_axis]
                    data_to_save = zip(*data_to_save)
                    writer.writerows(data_to_save)
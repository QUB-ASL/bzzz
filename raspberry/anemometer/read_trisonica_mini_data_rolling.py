#!/usr/bin/env python3
import serial
import numpy as np

all_data = []
wind_speed = []
wind_speed_2D = []
H_direction =[]
V_direction = []

for x in range(20):
   wind_speed.append(0.00)
   wind_speed_2D.append(0.00)
   H_direction.append(0.00)
   V_direction.append(0.00)

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
    ser.reset_input_buffer()

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)

            all_data = line.split()

            wind_speed = np.roll(wind_speed, 1)
            wind_speed_2D = np.roll(wind_speed_2D, 1)
            H_direction = np.roll(H_direction, 1)
            V_direction = np.roll(V_direction, 1)

            wind_speed[0] = float(all_data[0])
            wind_speed_2D[0] = float(all_data[1])
            H_direction[0] = float(all_data[2])
            V_direction[0] = float(all_data[3])

            #print(all_data)
            print(wind_speed)
            print(wind_speed_2D)
            print(H_direction)
            print(V_direction)
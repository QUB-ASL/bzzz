import pandas as pd
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from math import pi, atan2, sqrt
import numpy as np
from datetime import datetime


import bzzz.thread_this
import bzzz.read_sbus.read_sbus_from_GPIO_receiver
from bzzz.sensors.time_of_flight_sensor import TimeOfFlightSensor
from time import time_ns
from bzzz.scheduler import Scheduler

if __name__ == '__main__':
    tof = TimeOfFlightSensor(use_sleep=-1, num_latest_readings_to_keep=1, cache_altitude=True, use_outlier_detection=True, abs_outlier_diff_thres=500)
    rc = bzzz.read_sbus.RC()

    scheduler = Scheduler(use_threading=False)

    num_run = [9000]
    time_cache = []

    quat_cache = []
    yaw_cache = []
    pitch_cache = []
    roll_cache = []

    throttle_ref_cache = []
    accelrometer_cache = []
    time_before_thread_starts = 0


    quat = [0., 0., 0.]
    acc = [0., 0., 0.]
    euler = [0., 0., 0.]

    is_data_saved = False
    is_data_log_kill = [False]

    _, plts = plt.subplots(4, 2)

    
    def euler_angles(q):
        euler = [0., 0., 0.]

        sinr_cosp = 2 * (q[0] * q[1] + q[2] * q[3])
        cosr_cosp = 1 - 2 * (q[1] * q[1] + q[2] * q[2])
        euler[2] = atan2(sinr_cosp, cosr_cosp)

        # pitch (y-axis rotation)
        sinp = sqrt(1 + 2 * (q[0] * q[2] - q[1] * q[3]))
        cosp = sqrt(1 - 2 * (q[0] * q[2] - q[1] * q[3]))
        euler[1] = 2 * atan2(sinp, cosp) - pi / 2

        # yaw (z-axis rotation)
        siny_cosp = 2 * (q[0] * q[3] + q[1] * q[2])
        cosy_cosp = 1 - 2 * (q[2] * q[2] + q[3] * q[3])
        euler[0] = atan2(siny_cosp, cosy_cosp)

        return euler

    # def process_radio_data():
        # channel_data = rc.get_radio_data_parse_and_send_to_ESP(return_channel_date=True, force_send_fake_data=False, fake_data="S,0,0,0,0,0,0,0,0,0")
        # throttle_ref_cache.append(channel_data.strip().split(',')[3])
        # if rc.parser.kill():
            # altitude_cache_df = pd.DataFrame([[t, Tr, alt] for t, Tr, alt in zip(time_cache, throttle_ref_cache, tof.altitude_cache())])
            # altitude_cache_df.to_csv("/home/bzzz/Desktop/data_log.csv", index=False, header=False)
            # with open("/home/bzzz/Desktop/data_log.csv", "w") as file:
            #     file.write("time_stamps = %f,\n\n\n Throttle_reference = %f,\n\n\n altitude_cache = %f\n"%(time_cache, throttle_ref_cache, tof.altitude_cache()))
            # tof.kill_ToF()
            # altitude_logger_thread.cancel()
            # scheduler.kill("process_radio_data")
            # exit(0)
    
    def process_data():
        # process radio data
        channel_data = rc.get_radio_data_parse_and_send_to_ESP(return_channel_date=True, force_send_fake_data=False, fake_data="S,0,0,0,0,0,0,0,0,0")

        # process ESP data
        flight_data = rc.print_receive_data_from_ESP(return_data=True)
        # print(flight_data)
        if flight_data is not None and "FD:" in flight_data:
            flight_data = flight_data.strip().split()
            if len(flight_data) == 7:
                try:
                    is_data_log_kill[0] = rc.parser.kill()
                    throttle_ref_cache.append(channel_data.strip().split(',')[3])
			print(throttle_ref_cache[-1])
                    q1 = float(flight_data[1])
                    q2 = float(flight_data[2])
                    q3 = float(flight_data[3])
                    ax = float(flight_data[4])
                    ay = float(flight_data[5])
                    az = float(flight_data[6])

                    quat[0] = q1
                    quat[1] = q2
                    quat[2] = q3
                    acc[0] = ax
                    acc[1] = ay
                    acc[2] = az
                    euler = euler_angles([sqrt(1 - quat[0]**2 - quat[1]**2 - quat[2]**2)] + quat)
                    num_run[0] -= 1
                    print(num_run)

                    quat_cache.append(quat)
                    yaw_cache.append(euler[0])
                    pitch_cache.append(euler[1])
                    roll_cache.append(euler[2])
                    accelrometer_cache.append(acc[:])

                    temp = tof.altitude
                    if temp == -1:
                        print("ToF outlier or -ve distance detected, discarded the measurement.")
                    time_cache.append((time_ns() - time_before_thread_starts)/1000000)
                except Exception as e:
                    print("Exception in main.py: ", e)
                    pass
    def rad2deg(lst):
        return [i*180/pi for i in lst]
    time_before_thread_starts = time_ns()
    # scheduler.schedule("print_ESP_data", print_ESP_data, function_call_frequency=50, function_call_count=10000)
    scheduler.schedule("process_data", process_data, function_call_frequency=50, function_call_count=10000)
    while True:
        # print_ESP_data()
        # process_radio_data()
        scheduler.run()
        if not is_data_saved and (num_run[0] == 0 or is_data_log_kill[0]):
            print("saving data wait....")
            is_data_saved = True
            accelrometer_cache_ = np.array(accelrometer_cache)
            # altitude_logger_thread = bzzz.thread_this.run_thread_every_given_interval(0.02, run)
            # scheduler.kill("process_radio_data")
            # scheduler.kill("process_data")
            date_time_now = datetime.now()
            data_cache_df = pd.DataFrame([[t, Tr, y, p, r, alt, ax, ay, az] for t, Tr, y, p, r, alt, ax, ay, az 
                                          in zip(time_cache, throttle_ref_cache, yaw_cache, pitch_cache, roll_cache, 
                                                 tof.altitude_cache(), accelrometer_cache_[:, 0], accelrometer_cache_[:, 1], accelrometer_cache_[:, 2])])
            data_cache_df.to_csv(f"/home/bzzz/Desktop/data_log_{date_time_now.year}_{date_time_now.month}_{date_time_now.day}_{date_time_now.hour}:{date_time_now.minute}:{date_time_now.second}.csv", index=False, header=False)
            # with open("/home/bzzz/Desktop/data_log.csv", "w") as file:
            #    file.write("time_stamps = %f,\n\n\n Throttle_reference = %f,\n\n\n altitude_cache = %f\n"%(time_cache, throttle_ref_cache, tof.altitude_cache()))
            
            print(f"time: {time_cache} \naltitude: {tof.altitude_cache()} \nTref: {throttle_ref_cache} \nyaw: {yaw_cache} \npitch: {pitch_cache} \nroll:{roll_cache} \nacc: {accelrometer_cache_}")
            """plts[0, 0].plot(time_cache, throttle_ref_cache[:len(time_cache)])
            plts[1, 0].plot(time_cache, rad2deg(yaw_cache[:len(time_cache)+1]))
            plts[2, 0].plot(time_cache, rad2deg(pitch_cache[:len(time_cache)+1]))
            plts[3, 0].plot(time_cache, rad2deg(roll_cache[:len(time_cache)+1]))
            
            plts[0, 0].legend(["Throttle ref"])
            plts[1, 0].legend(["Yaw deg"])
            plts[2, 0].legend(["Pitch deg"])
            plts[3, 0].legend(["Roll deg"])
            plts[0, 0].set_xlabel("time ms")
            plts[1, 0].set_xlabel("time ms")
            plts[2, 0].set_xlabel("time ms")
            plts[3, 0].set_xlabel("time ms")
            plts[0, 0].set_ylabel("Throttle Ref")
            plts[1, 0].set_ylabel("Yaw")
            plts[2, 0].set_ylabel("Pitch")
            plts[3, 0].set_ylabel("Roll")

            plts[0, 1].plot(time_cache[:len(tof.altitude_cache())], tof.altitude_cache()[:-1])
            plts[1, 1].plot(time_cache, accelrometer_cache_[:len(time_cache), 0])
            plts[2, 1].plot(time_cache, accelrometer_cache_[:len(time_cache), 1])
            plts[3, 1].plot(time_cache, accelrometer_cache_[:len(time_cache), 2])
            
            plts[0, 1].legend(["Altitude mm"])
            plts[1, 1].legend(["Acc_x  g"])
            plts[2, 1].legend(["Acc_y g"])
            plts[3, 1].legend(["Acc_z g"])
            plts[0, 1].set_xlabel("time ms")
            plts[1, 1].set_xlabel("time ms")
            plts[2, 1].set_xlabel("time ms")
            plts[3, 1].set_xlabel("time ms")
            plts[0, 1].set_ylabel("Altitude Z")
            plts[1, 1].set_ylabel("Acc_x")
            plts[2, 1].set_ylabel("Acc_y")
            plts[3, 1].set_ylabel("Acc_z")

            plt.savefig("ToF_data_plot_with_pitch_and_roll.svg")"""
            # plt.show()
            tof.kill_ToF()
            print("Saving done!")
            # break

    
    

# Run the get_radio_data_parse_and_send_to_ESP funtionn @ 50Hz
# run_thread_every_given_interval(0.02, get_radio_data_parse_and_send_to_ESP)
# run_thread_every_given_interval(0.02, print_receive_data_from_ESP)
# time_before_thread_starts = time_ns()
# bzzz.thread_this.run_thread_every_given_interval(0.02, run)

import pandas as pd
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from math import pi, atan2, sqrt


import bzzz.thread_this
import bzzz.read_sbus.read_sbus_from_GPIO_receiver
from bzzz.sensors.time_of_flight_sensor import TimeOfFlightSensor
from time import time_ns
from bzzz.scheduler import Scheduler

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


if __name__ == '__main__':
    tof = TimeOfFlightSensor(use_sleep=-1, num_latest_readings_to_keep=1, cache_altitude=True)
    rc = bzzz.read_sbus.RC()

    scheduler = Scheduler(use_threading=False)

    num_run = [1000]
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

    _, plts = plt.subplots(4, 2)

    def process_radio_data():
        channel_data = rc.get_radio_data_parse_and_send_to_ESP(return_channel_date=True, force_send_fake_data=False, fake_data="S,0,0,0,0,0,0,0,0,0")
        throttle_ref_cache.append(channel_data.strip().split()[4])
        # if rc.parser.kill():
            # altitude_cache_df = pd.DataFrame([[t, Tr, alt] for t, Tr, alt in zip(time_cache, throttle_ref_cache, tof.altitude_cache())])
            # altitude_cache_df.to_csv("/home/bzzz/Desktop/data_log.csv", index=False, header=False)
            # with open("/home/bzzz/Desktop/data_log.csv", "w") as file:
            #     file.write("time_stamps = %f,\n\n\n Throttle_reference = %f,\n\n\n altitude_cache = %f\n"%(time_cache, throttle_ref_cache, tof.altitude_cache()))
            # tof.kill_ToF()
            # altitude_logger_thread.cancel()
            # scheduler.kill("process_radio_data")
            # exit(0)
    
    def print_ESP_data():
        flight_data = rc.print_receive_data_from_ESP(return_data=True)
        if flight_data is not None and "FD:" in flight_data:
            flight_data = flight_data.strip().split()
            if len(flight_data) == 7:
                try:
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

                    euler = euler_angles(quat)
                    num_run[0] -= 1
                    print(num_run)

                    quat_cache.append(quat)
                    yaw_cache.append(euler[0])
                    pitch_cache.append(euler[1])
                    roll_cache.append(euler[2])

                    accelrometer_cache.append(acc)

                    temp = tof.altitude
                    print(temp, float(flight_data[1])*180/pi, float(flight_data[2])*180/pi)
                    time_cache.append((time_ns() - time_before_thread_starts)/1000000)
                except:
                    pass
    def rad2deg(lst):
        return [i*180/pi for i in lst]
    time_before_thread_starts = time_ns()
    scheduler.schedule("print_ESP_data", print_ESP_data, 10, 10000)
    scheduler.schedule("process_radio_data", process_radio_data, 10, 10000)
    while True:
        # print_ESP_data()
        # process_radio_data()
        scheduler.run()
        if num_run[0] == 0:
            # altitude_logger_thread = bzzz.thread_this.run_thread_every_given_interval(0.02, run)
            scheduler.kill("process_radio_data")
            scheduler.kill("print_ESP_data")
            print(tof.altitude_cache(), time_cache, pitch_cache, roll_cache)
            plts[0, 0].plot(time_cache, throttle_ref_cache[:len(time_cache)])
            plts[0, 1].plot(time_cache, rad2deg(yaw_cache[:len(time_cache)+1]))
            plts[0, 2].plot(time_cache, rad2deg(pitch_cache[:len(time_cache)+1]))
            plts[0, 3].plot(time_cache, rad2deg(roll_cache[:len(time_cache)+1]))
            
            plts[0, 0].legend(["Throttle ref"])
            plts[0, 1].legend(["Yaw deg"])
            plts[0, 2].legend(["Pitch deg"])
            plts[0, 3].legend(["Roll deg"])
            plts[0, 0].set_xlabel("time ms")
            plts[0, 1].set_xlabel("time ms")
            plts[0, 2].set_xlabel("time ms")
            plts[0, 3].set_xlabel("time ms")
            plts[0, 0].set_ylabel("Throttle Ref")
            plts[0, 1].set_ylabel("Yaw")
            plts[0, 2].set_ylabel("Pitch")
            plts[0, 3].set_ylabel("Roll")

            plts[1, 0].plot(time_cache, tof.altitude_cache()[:len(time_cache)])
            plts[1, 1].plot(time_cache, accelrometer_cache[:len(time_cache)][0])
            plts[1, 2].plot(time_cache, accelrometer_cache[:len(time_cache)][1])
            plts[1, 3].plot(time_cache, accelrometer_cache[:len(time_cache)][2])
            
            plts[1, 0].legend(["Altitude mm"])
            plts[1, 1].legend(["Acc_x  g"])
            plts[1, 2].legend(["Acc_y g"])
            plts[1, 3].legend(["Acc_z g"])
            plts[1, 0].set_xlabel("time ms")
            plts[1, 1].set_xlabel("time ms")
            plts[1, 2].set_xlabel("time ms")
            plts[1, 3].set_xlabel("time ms")
            plts[1, 0].set_ylabel("Altitude Z")
            plts[1, 1].set_ylabel("Acc_x")
            plts[1, 2].set_ylabel("Acc_y")
            plts[1, 3].set_ylabel("Acc_z")

            plt.savefig("ToF_data_plot_with_pitch_and_roll.svg")
            plt.show()
            tof.kill_ToF()

            data_cache_df = pd.DataFrame([[t, Tr, y, p, r, alt, ax, ay, az] for t, Tr, y, p, r, alt, ax, ay, az 
                                          in zip(time_cache, throttle_ref_cache, yaw_cache, pitch_cache, roll_cache, 
                                                 tof.altitude_cache(), accelrometer_cache[:][0], accelrometer_cache[:][1], accelrometer_cache[:][2])])
            data_cache_df.to_csv("/home/bzzz/Desktop/data_log.csv", index=False, header=False)
            with open("/home/bzzz/Desktop/data_log.csv", "w") as file:
                file.write("time_stamps = %f,\n\n\n Throttle_reference = %f,\n\n\n altitude_cache = %f\n"%(time_cache, throttle_ref_cache, tof.altitude_cache()))

            break

    
    

# Run the get_radio_data_parse_and_send_to_ESP funtionn @ 50Hz
# run_thread_every_given_interval(0.02, get_radio_data_parse_and_send_to_ESP)
# run_thread_every_given_interval(0.02, print_receive_data_from_ESP)
# time_before_thread_starts = time_ns()
# bzzz.thread_this.run_thread_every_given_interval(0.02, run)
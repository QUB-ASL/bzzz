import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from math import pi


import bzzz.thread_this
import bzzz.read_sbus.read_sbus_from_GPIO_receiver
from bzzz.sensors.time_of_flight_sensor import TimeOfFlightSensor
from time import time_ns
from bzzz.scheduler import Scheduler

if __name__ == '__main__':
    tof = TimeOfFlightSensor(use_sleep=-1, num_latest_readings_to_keep=5, cache_altitude=True)
    rc = bzzz.read_sbus.RC()

    scheduler = Scheduler(use_threading=False)

    num_run = [1000]
    time_cache = []
    throttle_ref_cache = []
    pitch_cache = []
    roll_cache = []
    time_before_thread_starts = 0

    _, plts = plt.subplots(3, 1)

    def process_radio_data():
        channel_data = rc.get_radio_data_parse_and_send_to_ESP(return_channel_date=True, force_send_fake_data=False, fake_data="S,0,0,0,0,0,0,0,0,0")
        # throttle_ref_cache.append(channel_data[3])
        # throttle_ref_cache.append(1)
        # temp = tof.altitude
        # print(throttle_ref_cache[-1], temp)
        # print(temp)
        # time_cache.append((time_ns() - time_before_thread_starts)/1000000)
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
        pr_data = rc.print_receive_data_from_ESP(return_data=True)
        if pr_data is not None and "PR:" in pr_data:
            pr_data = pr_data.strip().split()
            if len(pr_data) == 3:
                try:
                    float(pr_data[1])
                    float(pr_data[2])
                    num_run[0] -= 1
                    print(num_run)
                    pitch_cache.append(float(pr_data[1]))
                    roll_cache.append(float(pr_data[2]))
                    temp = tof.altitude
                    print(temp)
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
            plts[0].plot(time_cache, tof.altitude_cache()[:len(time_cache)])
            plts[1].plot(time_cache, rad2deg(pitch_cache[:len(time_cache)+1]))
            plts[2].plot(time_cache, rad2deg(roll_cache[:len(time_cache)+1]))
            plts[0].legend(["altitude mm"])
            plts[1].legend(["pitch deg"])
            plts[2].legend(["roll deg"])
            plts[0].set_xlabel("time ms")
            plts[1].set_xlabel("time ms")
            plts[2].set_xlabel("time ms")
            plts[0].set_ylabel("altitude Z")
            plts[1].set_ylabel("Pitch")
            plts[2].set_ylabel("Roll")
            plt.show()
            break
            # tof.kill_ToF()

    
    

# Run the get_radio_data_parse_and_send_to_ESP funtionn @ 50Hz
# run_thread_every_given_interval(0.02, get_radio_data_parse_and_send_to_ESP)
# run_thread_every_given_interval(0.02, print_receive_data_from_ESP)
# time_before_thread_starts = time_ns()
# bzzz.thread_this.run_thread_every_given_interval(0.02, run)
import bzzz.thread_this
import bzzz.read_sbus.read_sbus_from_GPIO_receiver
from bzzz.sensors.time_of_flight_sensor import TimeOfFlightSensor
from time import time_ns


def main():
    tof = TimeOfFlightSensor(use_sleep=True, cache_altitude=True)
    print(tof)

    while True:
        print(tof.altitude)
    # rc = bzzz.read_sbus.RC()

    # time_cache = []
    # throttle_ref_cache = []
    # time_before_thread_starts = 0

    # def run():
        
    #     channel_data = rc.get_radio_data_parse_and_send_to_ESP(return_channel_date=True).split(",")
    #     throttle_ref_cache.append(channel_data[4])
    #     temp = tof.altitude
    #     time_cache.append((time_ns() - time_before_thread_starts)/1000000)
    #     if rc.parser.kill():
    #         with open("/home/bzzz/Desktop/data_log.csv", "w") as file:
    #             file.write("time_stamps = %f,\n\n\n Throttle_reference = %f,\n\n\n altitude_cache = %f\n"%(time_cache, throttle_ref_cache, tof.altitude_cache()))
    #             tof.kill_ToF()
    #         exit(0)
    
    # time_before_thread_starts = time_ns()
    # bzzz.thread_this.run_thread_every_given_interval(0.02, run)

if __name__ == '__main__':
    main() 
    
    

# Run the get_radio_data_parse_and_send_to_ESP funtionn @ 50Hz
# run_thread_every_given_interval(0.02, get_radio_data_parse_and_send_to_ESP)
# run_thread_every_given_interval(0.02, print_receive_data_from_ESP)
# time_before_thread_starts = time_ns()
# bzzz.thread_this.run_thread_every_given_interval(0.02, run)
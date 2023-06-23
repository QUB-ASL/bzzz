from thread_this import run_thread_every_given_interval
from read_sbus.read_sbus_from_GPIO_receiver import get_radio_data_parse_and_send_to_ESP, parser
from sensors.time_of_flight_sensor import TimeOfFlightSensor
from time import time_ns


tof = TimeOfFlightSensor(use_sleep=False, cache_altitude=True)

time_cache = []
throttle_ref_cache = []
time_before_thread_starts = 0

def run():
    channel_data = get_radio_data_parse_and_send_to_ESP(return_channel_date=True).split(",")
    throttle_ref_cache.append(channel_data[4])
    temp = tof.altitude
    time_cache.append((time_ns() - time_before_thread_starts)/1000000)
    if parser.kill():
        with open("/home/bzzz/Desktop/data_log.csv", "w") as file:
            file.write("time_stamps = %f,\n\n\n Throttle_reference = %f,\n\n\n altitude_cache = %f\n"%(time_cache, throttle_ref_cache, tof.altitude_cache()))
            tof.kill_ToF()
        exit(0)

    

# Run the get_radio_data_parse_and_send_to_ESP funtionn @ 50Hz
# run_thread_every_given_interval(0.02, get_radio_data_parse_and_send_to_ESP)
# run_thread_every_given_interval(0.02, print_receive_data_from_ESP)
time_before_thread_starts = time_ns()
run_thread_every_given_interval(0.02, run)
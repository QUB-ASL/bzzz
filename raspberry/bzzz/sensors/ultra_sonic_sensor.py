# TODO: implement proper code for a particular sensor
# TODO: add proper Doc strings
# NOTE: for now, we are just passing dummy values

from filters import median_filter
from time import time_ns, sleep
import board
from adafruit_hcsr04 import HCSR04

class Sonar:
    def __init__(self, num_latest_readings_to_keep: int = 5, use_sleep=False, sleep_time = 0.02, trigger_pin=board.D17, echo_pin=board.D27):
        self._current_altitude = None
        self._altitude_readings_list = None
        self._altitude_readings_list_current_index = None
        self._num_latest_readings_to_keep = num_latest_readings_to_keep
        
        self._previous_altitude = None
        self._last_update_time = None
        self.use_sleep = use_sleep
        self.sleep_time = sleep_time

        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin

        self._init_sonar()

    def _init_sonar(self):
        print("Init Ultra-sonic sensor, wait.....")
        self.sonar = HCSR04(trigger_pin=self.trigger_pin, echo_pin=self.echo_pin)
        self._last_update_time = time_ns()
        self._altitude_readings_list = list()
        self._altitude_readings_list_current_index = 0
        for _ in range(self._num_latest_readings_to_keep):
            self._altitude_readings_list.append(self._get_current_sonar_measurement())
            sleep(self.sleep_time)
        self.update_altitude()
        print("Init  Ultra-sonic sensor, Done!")

    @property
    def altitude(self):
        self.update_altitude()
        return self._current_altitude
    
    @altitude.setter
    def altitude(self, val):
        self._current_altitude = val

    def _get_current_sonar_measurement(self):
        # TODO: add code to get measurement from sensor
        sonar_distance_reading = self.sonar.distance
        return sonar_distance_reading

    def _update_sonar(self):
        ToF_distance_reading = self._get_current_sonar_measurement()  # dummy value for now, actually should have a proper value
        if ToF_distance_reading < 0:
            return -1
        self._altitude_readings_list[self._altitude_readings_list_current_index] = ToF_distance_reading
        if 0 <= self._altitude_readings_list_current_index < self._num_latest_readings_to_keep - 1:
            self._altitude_readings_list_current_index += 1
        else:
            self._altitude_readings_list_current_index = 0
        self._current_altitude = median_filter(self._altitude_readings_list, self._num_latest_readings_to_keep)

    def update_altitude(self):
        if not self.use_sleep:
            if time_ns() - self._last_update_time > self.sleep_time*10**9:
                temp = self._current_altitude
                if self._update_sonar() != -1:
                    self._previous_altitude = temp
                else:
                    print("ToF sensor returning -ve distance....\nretrying....")
                self._last_update_time = time_ns()
        else:
            temp = self._current_altitude
            if self._update_sonar() != -1:
                self._previous_altitude = temp
            else:
                print("ToF sensor returning -ve distance....\nretrying....")
            sleep(self.sleep_time)
        
    def kill(self):
        print("Killing sonar, wait...")
        self.sonar.deinit()
        print("Killed sonar.")


if __name__ == "__main__":
    sonar = Sonar(use_sleep=True)
    for i in range(100):
        sonar.update_altitude()
        print("Altitude in cm: %d   itr: %d" %(sonar.altitude, i))
    sonar.kill()
    

        
        
          
    
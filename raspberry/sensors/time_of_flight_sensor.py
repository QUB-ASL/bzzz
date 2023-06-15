# TODO: implement proper code for a particular sensor
# TODO: add proper Doc strings
# NOTE: for now, we are just passing dummy values

from filters import median_filter
from time import time_ns, sleep, time
from datetime import datetime
import VL53L0X
import os 

class TimeOfFlightSensor:
    def __init__(self, num_latest_readings_to_keep: int = 5, use_sleep=False):
        self._current_altitude = None
        self._altitude_readings_list = None
        self._altitude_readings_list_current_index = None
        self._num_latest_readings_to_keep = num_latest_readings_to_keep
        
        self._previous_altitude = None
        self._last_update_time = None
        self.use_sleep = use_sleep
        self._init_ToF_sensor()

    def _init_ToF_sensor(self, address=0x29, mode=VL53L0X.Vl53l0xAccuracyMode.BEST):
        print("Init ToF, wait.....")
        self.tof = VL53L0X.VL53L0X(i2c_bus=1,i2c_address=address)        
        self.tof.open()
        self.tof.start_ranging(mode=mode)
        self.timing = self.tof.get_timing()
        if self.timing < 20000:
            self.timing = 20000
        self._last_update_time = time_ns()
        self._altitude_readings_list = list()
        self._altitude_readings_list_current_index = 0
        for _ in range(self._num_latest_readings_to_keep):
            self._altitude_readings_list.append(self._get_current_ToF_measurement())
            sleep(self.timing/1000000.0)
        self.update_altitude()
        print("Init ToF, Done!")

    @property
    def altitude(self):
        self.update_altitude()
        return self._current_altitude
    
    @altitude.setter
    def altitude(self, val):
        self._current_altitude = val

    def _get_current_ToF_measurement(self):
        # TODO: add code to get measurement from sensor
        ToF_distance_reading = self.tof.get_distance()
        return ToF_distance_reading

    def _update_ToF(self):
        ToF_distance_reading = self._get_current_ToF_measurement()  # dummy value for now, actually should have a proper value
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
            if time_ns() - self._last_update_time > self.timing*1000:
                temp = self._current_altitude
                if self._update_ToF() != -1:
                    self._previous_altitude = temp
                else:
                    print("ToF sensor returning -ve distance....\nretrying....")
                self._last_update_time = time_ns()
        else:
            temp = self._current_altitude
            if self._update_ToF() != -1:
                self._previous_altitude = temp
            else:
                print("ToF sensor returning -ve distance....\nretrying....")
            sleep(self.timing/1000000)
        
    def kill_ToF(self):
        print("Killing ToF, wait...")
        self.tof.stop_ranging()
        self.tof.close()
        print("Killed Tof.")


if __name__ == "__main__":
    tof = TimeOfFlightSensor(use_sleep=True)
    with open("/home/bzzz/Desktop/data_log.csv", "w") as file:
        for i in range(100):
            tof.update_altitude()
            print("Altitude in mm: %d   itr: %d" %(tof.altitude, i))
            file.write("%f, %f\n"%(i, tof.altitude))
    tof.kill_ToF()  

    

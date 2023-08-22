from bzzz.sensors.filters import median_filter
from time import time_ns, sleep
from datetime import datetime
import VL53L0X
import os


class TimeOfFlightSensor:
    # NOTE: This class fetches altitude in millimeters and this class requires i2c interfacing with the sensor.
    def __init__(self,
                 median_filter_length = 3,
                 update_measurement_at_fixed_rate=False,
                 cache_altitude=False,
                 use_outlier_detection=False,
                 abs_outlier_diff_thres=500):
        """Time of flight sensor class initialization.

        :param median_filter_length: Window length for median filter, defaults to 3
        :param update_measurement_at_fixed_rate: Indicator to use difference between current time and last measurement time
          and wait till sufficient time is elapsed to take a measurement, defaults to False
        :param cache_altitude: Cache the altitude measurements in mm if True, defaults to False
        :param use_outlier_detection: Use outlier detection based on maximum alowable altitude change, defaults to False
        :param abs_outlier_diff_thres: Maximum change in altitude allowed between the current and previous measurements, defaults to 500
        """
        # Latest measurment update variables.
        self._current_altitude = None
        self._altitude_readings_list = None
        self._altitude_readings_list_current_index = None
        self._median_filter_length = median_filter_length

        # previous measurement varaibles.
        self._previous_altitude = None
        self._last_update_time = None
        self.update_measurement_at_fixed_rate = update_measurement_at_fixed_rate

        # Data cache varaibles.
        self.cache_altitude = cache_altitude
        self._altitude_cache = []

        # outlier detection varaibles.
        self.use_outlier_detection = use_outlier_detection
        self.__abs_outlier_diff_thres = abs_outlier_diff_thres

        # Call for sensor initialization.
        self.__init_ToF_sensor()

    def __init_ToF_sensor(self,
                          address=0x29,
                          mode=VL53L0X.Vl53l0xAccuracyMode.LONG_RANGE):
        """Function to initialize the ToF sensor.

        :param address: ToF sensor physical i2C address, defaults to 0x29
        :param mode: Sensor mode of operation, defaults to VL53L0X.Vl53l0xAccuracyMode.LONG_RANGE
        """
        print("Init ToF, wait.....")
        self.tof = VL53L0X.VL53L0X(i2c_bus=1, i2c_address=address)
        self.tof.open()
        self.tof.start_ranging(mode=mode)
        self.timing = self.tof.get_timing()
        if self.timing < 20000:
            self.timing = 20000
        self._last_update_time = time_ns()
        self._altitude_readings_list = list()
        self._altitude_readings_list_current_index = 0
        for _ in range(self._median_filter_length):
            self._altitude_readings_list.append(
                self.__get_current_ToF_measurement())
            sleep(self.timing/1000000.0)
        self.__update_altitude()
        print("Init ToF, Done!")

    @property
    def abs_outlier_diff_thres(self):
        """return the current setting of absolute outlier difference threshold.

        :return: absolute outlier difference threshold.
        """
        return self.__abs_outlier_diff_thres

    @abs_outlier_diff_thres.setter
    def abs_outlier_diff_thres(self, threshold):
        """Setter for absolute outlier difference threshold

        :param threshold: new threshold value.
        """
        self.__abs_outlier_diff_thres = threshold

    @property
    def altitude(self):
        """Updates and returns the current altitude measurement in mm.

        :return: If there is no measurement error the function returns the current altitude measurement in mm else -1.
        """
        status = self.__update_altitude()
        if status == -1:
            return -1
        return self._current_altitude

    def altitude_cache(self):
        """Returns altitude cache list.

        :return: altitude cache list.
        """
        return self._altitude_cache

    def __get_current_ToF_measurement(self):
        """Fetches the latest ToF sensor measurement.

        :return: latest altitude measurement in mm.
        """
        ToF_distance_reading = self.tof.get_distance()
        return ToF_distance_reading

    def __update_ToF(self):
        """Fetches latest ToF measurement. Updates altitude measurement based on outlier detection and/ median fliter.

        :return: -1 if there is an outlier or sudden change in altitude which is greater than absolute outlier difference threshold 
        or sensor is not working properly.
        """
        ToF_distance_reading = self.__get_current_ToF_measurement()
        if ToF_distance_reading < 0 or (self.use_outlier_detection and (abs(ToF_distance_reading - (self._current_altitude if self._current_altitude is not None else 500)) > self.__abs_outlier_diff_thres)):
            return -1
        self._altitude_readings_list[self._altitude_readings_list_current_index] = ToF_distance_reading
        if 0 <= self._altitude_readings_list_current_index < self._median_filter_length - 1:
            self._altitude_readings_list_current_index += 1
        else:
            self._altitude_readings_list_current_index = 0
        self._current_altitude = median_filter(
            self._altitude_readings_list, self._median_filter_length)

    def __update_altitude(self):
        """Updates the Altitude measurement in mm.

        :return: None if valid measurement is taken. -1 otherwise.
        """
        time_now = time_ns()
        # if update_measurement_at_fixed_rate is False take and return measurement instantly
        if not self.update_measurement_at_fixed_rate:
            temp = self._current_altitude
            if self.__update_ToF() != -1:
                self._previous_altitude = temp
                if self.cache_altitude:
                    self._altitude_cache.append(self._current_altitude)
            else:
                if self.cache_altitude:
                    self._altitude_cache.append(-1)
                print("ToF sensor returning -ve distance....\nretrying....")
                return -1
            self._last_update_time = time_now
            return
        else:
            # if update_measurement_at_fixed_rate is True take and return measurement based on time elapsed
            if time_now - self._last_update_time > self.timing*1000:
                temp = self._current_altitude
                if self.__update_ToF() != -1:
                    self._previous_altitude = temp
                    if self.cache_altitude:
                        self._altitude_cache.append(self._current_altitude)
                else:
                    if self.cache_altitude:
                        self._altitude_cache.append(-1)
                    print("ToF sensor returning -ve distance....\nretrying....")
                    return -1
                self._last_update_time = time_now

    def kill_ToF(self):
        """Kill the ToF sensor. 
        NOTE: After killing the sensor will stop measuring the altitude. It needs to be reinitialized to start measuring again.
        """
        print("Killing ToF, wait...")
        self.tof.stop_ranging()
        self.tof.close()
        print("Killed ToF")


# Test script.
if __name__ == "__main__":
    tof = TimeOfFlightSensor(update_measurement_at_fixed_rate=True)
    time_before_loop_starts = time_ns()
    with open("/home/bzzz/Desktop/data_log.csv", "w") as file:
        for i in range(100):
            print("Altitude in mm: %d   itr: %d" % (tof.altitude, i))
            file.write("%f, %f, %f\n" % (
                (time_ns() - time_before_loop_starts)/1000000, i, tof.altitude))
    tof.kill_ToF()

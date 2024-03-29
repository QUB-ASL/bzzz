import numpy as np  # for matrix based calculations
import pandas as pd  # pandas for storing cached data into csv files

from time import time_ns  # function to get system-up time in nano seconds
from datetime import datetime  # to get date-time stamps for naming the csv files
from math import pi, atan2, sqrt  # math functions for calculations

from bzzz.controllers.altitude_LQR import LQR  # altitude hold controller
from bzzz.estimators.altitude_Kalman_filter import KalmanFilter
from bzzz.scheduler import Scheduler
from bzzz.sensors.time_of_flight_sensor import TimeOfFlightSensor
from bzzz.read_sbus import RC  # for radio data receiving, encoding and sending to ESP

from bzzz.sensors.evo_time_of_flight import EvoSensor
from bzzz.sensors.pressure_sensor import PressureSensor
from bzzz.sensors.anemometer import Anemometer
from bzzz.sensors.gnss import Gnss
from bzzz.sensors.data_logger import DataLogger
from bzzz.sensors.filters import NoFilter
from bzzz.sensors.filters import MedianFilter
from bzzz.sensors.filters import AverageFilter
import datetime



# NOTE: The scheduler supports both multi-threading and time-based function calling
# Although threading guarantees consistent function call rates, the actual process handling is not done
# within the python environment which could cause unwanted behaviour.

if __name__ == '__main__':
    # sampling frequency of KF and LQR
    sampling_frequency = 50
    # caching configuration
    enable_caching = [True]
    enable_printing_cache_to_screen = [False and enable_caching[0]]

    # objects declaration
    kf = KalmanFilter(sampling_frequency=sampling_frequency,
                      initial_Tt=0,
                      x_tilde_0=np.array([[0], [0], [10], [-9.81]]),
                      P_0=np.diagflat([1, 1, 1, 0.01]),
                      cache_values=True)
    lqr = LQR(sampling_frequency=sampling_frequency,
              initial_alpha_t=10,
              initial_beta_t=-9.81)
    # update_measurement_at_fixed_rate: if True then use time difference between current time and last measurement time to take a measurement
    #            if false then take a measurement instantly
    tof = EvoSensor(serial_path='/dev/ttyAMA2',
                     baud=115200,
                     window_length=3,
                     data_processor=MedianFilter(),
                     log_file=None,
                     max_samples=100000)
    rc = RC()
    scheduler = Scheduler(use_threading=False)

    # NOTE: single element lists are used to avoid python-env re-declaring
    # new local variables with in the functions that follow below.
    # data caching and logging
    time_cache = []
    quat_cache = []
    yaw_cache = []
    pitch_cache = []
    roll_cache = []
    motor_PWM_cache = []
    throttle_ref_cache = []
    accelerometer_cache = []
    altitude_reference_cache_mts = []
    radio_data_cache = []
    KF_data_cache = []
    time_before_thread_starts = [0]

    quaternion_vector = [0., 0., 0.]
    acc = [0., 0., 0.]
    euler = [0., 0., 0.]
    motor_PWM = [0., 0., 0., 0.]  # FL, FR, BL, BR
    channel_data = [""]
    KF_data = [0., 0., 0., 0.]

    # These variables are used to keep track of data logging process
    # indicates the position of switch A on the Remote.
    # This switch is used to save the logged data. Value is updated in `process_radio_data`
    switch_a_status = [True]
    # indicates the position of switch D. This is the kill switch on the Remote.
    # Value is updated in `process_radio_data`.
    # NOTE: you will have to kill the drone first before saving data.
    is_kill = [False]
    # indicates if data logging is allowed. Value is updated in the `main` loop.
    # Value update logic:
    # 1. Allow data logging for the first time by flipping switch A to on position.
    # 2. After saving the data for the first time, disable data logging.
    # 3. Now set the value to `not switch_A_status`, this disables the logging as long as
    #       switch A stays on. You will have to flip switch A off to re-enable data logging.
    allow_data_logging = [True]

    # Altitude hold vars
    throttle_ref_from_LQR = [0.]
    use_altitude_hold = [False]
    Tref_t = [0.0]
    altitude_ref_mts = [0.09]
    current_altitude_snap_shot_mts = [0.0]
    is_current_altitude_snap_shot_taken = [False]
    var_e_RC_mid_percentage = [0.5]
    altitude_shifter_range_mts = [0.5]
    is_drone_flying_close_to_ground = [False]
    min_altitude_to_activate_AltiHold_mts = [0.103]
    is_KF_ran_atleast_once = [False]
    last_valid_altitude_measurement_mts = [0.]
    max_consecutive_altitude_outliers_count = [10]
    num_consecutive_altitude_outliers_count_thus_far = [0]
    z_hat = [0.]
    v_hat = [0.]
    alpha_hat = [10.]
    beta_hat = [-9.81]
    gain_kp_from_rc = [0.]
    gain_kd_from_rc = [0.]
    KP_GAIN_MAX = 0.1  # 100
    KD_GAIN_MAX = 0.2  # 100

    DEBUG_MODE = False

    def print_debug(stuff):
        if DEBUG_MODE:
            print(stuff)

    # function to convert radians to degrees

    def rad2deg(lst):
        """Converts a list of angles in radians to a list of angles in degrees

        :param lst: list of angles in radians
        :return: list of angles in degrees
        """
        return [i*180/pi for i in lst]

    # function to compute quaternions to euler angles
    def euler_angles(q: list):
        """Computes euler angles from given quaternion

        :param q: Quaternion list [q0, q1, q2, q3]
        :return: list of euler angles [yaw, pitch, roll]
        """
        euler_ = [0., 0., 0.]

        sinr_cosp = 2 * (q[0] * q[1] + q[2] * q[3])
        cosr_cosp = 1 - 2 * (q[1] * q[1] + q[2] * q[2])
        euler_[2] = atan2(sinr_cosp, cosr_cosp)

        # pitch (y-axis rotation)
        sinp = sqrt(1 + 2 * (q[0] * q[2] - q[1] * q[3]))
        cosp = sqrt(1 - 2 * (q[0] * q[2] - q[1] * q[3]))
        euler_[1] = 2 * atan2(sinp, cosp) - pi / 2

        # yaw (z-axis rotation)
        siny_cosp = 2 * (q[0] * q[3] + q[1] * q[2])
        cosy_cosp = 1 - 2 * (q[2] * q[2] + q[3] * q[3])
        euler_[0] = atan2(siny_cosp, cosy_cosp)

        return euler_

    # function to cache all values at a time
    def cache_values():
        """Caches values if enable caching[0] is true
        """
        if enable_caching[0]:
            throttle_ref_cache.append(Tref_t[0])
            quat_cache.append(quaternion_vector[:])
            yaw_cache.append(euler[0])
            pitch_cache.append(euler[1])
            roll_cache.append(euler[2])
            motor_PWM_cache.append(motor_PWM[:])
            accelerometer_cache.append(acc[:])
            time_cache.append(
                (time_ns() - time_before_thread_starts[0])/1000000)
            altitude_reference_cache_mts.append(
                altitude_ref_mts[0] if use_altitude_hold[0] and not is_drone_flying_close_to_ground[0] else -1)
            KF_data_cache.append(KF_data[:])
            radio_data_cache.append(channel_data[0])

    # function to process radio data
    def process_radio_data():
        """This function does three jobs:
        1. Reads the radio data from the receiver, parses it and sends the 
           encoded data to ESP using a function from RC class.
        2. Updates shared variable values using radio data.
        3. Calls cache_values function.
        """
        # if altitude hold is enabled and drone is not close to the ground update the altitude_ref_mts
        if use_altitude_hold[0] and not is_drone_flying_close_to_ground[0]:
            altitude_ref_mts[0] = current_altitude_snap_shot_mts[0] + (
                var_e_RC_mid_percentage[0] - rc.trimmer_VRE_percentage())*altitude_shifter_range_mts[0]
            # the altitude_ref_mts should not be less than minimum flight altitude
            altitude_ref_mts[0] = max(
                min_altitude_to_activate_AltiHold_mts[0], altitude_ref_mts[0])

        # read, encode, and send the radio data to ESP.
        # if altitude hold is on the throttle value from the RC will be overwritten
        # by the throttle reference from the LQR.
        # NOTE: There is this weird conversion for LQR throttle reference below,
        # this is because the PI needs to send throttle reference in the range [300, 1400],
        # which is the actual range of the RC throttle stick.
        shift = int((throttle_ref_from_LQR[0] - 1000) * 1400/900 +
                   300) if use_altitude_hold[0] and not is_drone_flying_close_to_ground[0] else -1
        channel_data[0] = rc.get_radio_data_parse_and_send_to_ESP(return_channel_data=True,
                                                                  force_send_fake_data=False,
                                                                  fake_data="S,0,0,0,0,0,0,0,0,0",
                                                                  over_write_throttle_ref_to=shift)
        # update shared variables using RC data
        # is data logging killed and data saving requested?
        # is altitude hold enabled?
        switch_a_status[0] = rc.switch_A()
        use_altitude_hold[0] = rc.switch_C()
        is_kill[0] = rc.switch_D()
        # Kappa11 gain from RC
        gain_kp_from_rc[0] = rc.trimmer_VRA_percentage()*KP_GAIN_MAX
        # kappa22 gain from RC
        gain_kd_from_rc[0] = rc.trimmer_VRB_percentage()*KD_GAIN_MAX
        # normalised throttle reference from RC, max is 1900
        Tref_t[0] = (rc.throttle_reference_percentage() - 1000)/900
        cache_values()  # call to cache values

    def process_ESP_data():
        """Process ESP data, this function does two jobs:
        1. Receives flight data as a string of space separated values formatted as "FD: q1 q2 q3 ax ay az".
        2. Checks the received flight data for corruption. 
           If string is not None and starts with "FD:", and if there are 7 space separated values
           then convert the 7 values to floats and update shared variables.
        """
        # process ESP data
        flight_data_string = rc.receive_data_from_ESP()
        if flight_data_string is not None and "FD:" in flight_data_string:
            flight_data = flight_data_string.strip().split()
            if len(flight_data) == 11:

                # See if ALL the quaternion values are correct ...
                try:
                    q1 = float(flight_data[1])
                    q2 = float(flight_data[2])
                    q3 = float(flight_data[3])
                except ValueError as e:
                    print(
                        f"Invalid quaternion data from ESP32 - flight data: {flight_data_string}\n {e}")
                    return

                # ... if they are, then update
                quaternion_vector[0] = q1
                quaternion_vector[1] = q2
                quaternion_vector[2] = q3

                # additional check: if ESP is not armed, it sends [-1, -1, -1] for quaternions, which is invalid.
                if quaternion_vector == [-1., -1., -1.]:
                    print_debug(
                        f"Received quat = {quaternion_vector}; defaulting to quat = [0, 0, 0].")
                    quaternion_vector[0] = 0.
                    quaternion_vector[1] = 0.
                    quaternion_vector[2] = 0.

                # compute the scalar part of the quaternion
                q0 = sqrt(
                    1 - quaternion_vector[0]**2 - quaternion_vector[1]**2 - quaternion_vector[2]**2)
                quaternion_full = [q0] + quaternion_vector
                # compute euler angles from quaternion
                euler[0], euler[1], euler[2] = euler_angles(quaternion_full)

                try:
                    # convert flight data from string to floats
                    acc[0] = float(flight_data[4])
                    acc[1] = float(flight_data[5])
                    acc[2] = float(flight_data[6])
                    motor_PWM[0] = float(flight_data[7])
                    motor_PWM[1] = float(flight_data[8])
                    motor_PWM[2] = float(flight_data[9])
                    motor_PWM[3] = float(flight_data[10])
                except ValueError as e:
                    print(
                        f"Invalid data from ESP32 - flight data: {flight_data_string}\n {e}")

    def clear_caches():
        time_cache.clear()
        quat_cache.clear()
        yaw_cache.clear()
        pitch_cache.clear()
        roll_cache.clear()
        motor_PWM_cache.clear()
        throttle_ref_cache.clear()
        accelerometer_cache.clear()
        altitude_reference_cache_mts.clear()
        radio_data_cache.clear()
        KF_data_cache.clear()

    def read_ToF_run_kf_and_LQR():
        """Read ToF sensor, and run the Kalman filter and LQR control algorithms
        """

        # NOTE: DO NOT DIVIDE distance__from_tof_sensor BY 1000 here to get altitude measurements in m.
        # There are checks if distance__from_tof_sensor == -1 in the code for outlier detection.
        # you can run LQR even when the drone is close to ground but you cannot run KF.
        # So, to compensate use the previous estimates of alpha and beta
        # and the current ToF sensor readings. In this case if the ToF returns outliers
        # send current altitude as desired altitude to LQR so it has no control.

        # Reading the tof altitude invokes the automatic update from the sensor,
        # no need to read the sensor explicitly
        distance__from_tof_sensor = tof.distance

        if distance__from_tof_sensor == -1:
            print("ToF outlier or -ve distance detected, discarded the measurement.")
            num_consecutive_altitude_outliers_count_thus_far[0] += 1
        else:
            num_consecutive_altitude_outliers_count_thus_far[0] = 0
            last_valid_altitude_measurement_mts[0] = distance__from_tof_sensor /1000

        if num_consecutive_altitude_outliers_count_thus_far[0] == max_consecutive_altitude_outliers_count[0]:
            print(f"Something wrong with the ToF, maximum number of consecutive altitude outliers recorded: {num_consecutive_altitude_outliers_count_thus_far[0]}."
                  "".format("\n   **It is recommended to use manual mode in this situation**." if use_altitude_hold[0] else ""))

        is_drone_flying_close_to_ground[0] = last_valid_altitude_measurement_mts[0] < min_altitude_to_activate_AltiHold_mts[0]

        if is_drone_flying_close_to_ground[0]:
            z_hat[0] = current_altitude_snap_shot_mts[0] if distance__from_tof_sensor  == - \
                1 else distance__from_tof_sensor /1000
            print_debug(
                f"Cannot activate altitude hold. Drone is flying close to the ground at {last_valid_altitude_measurement_mts[0]/1000} mts < {min_altitude_to_activate_AltiHold_mts[0]} mts.")
            if is_KF_ran_atleast_once[0]:
                kf.reset()
        else:
            x_est = kf.update(Tref_t[0], euler[1], euler[2],
                              np.nan if distance__from_tof_sensor  == -1 else distance__from_tof_sensor /1000)
            is_KF_ran_atleast_once[0] = True
            z_hat[0] = x_est[0][0]
            v_hat[0] = x_est[1][0]
            alpha_hat[0] = x_est[2][0]
            beta_hat[0] = x_est[3][0]

            KF_data[0] = z_hat[0]
            KF_data[1] = v_hat[0]
            KF_data[2] = alpha_hat[0]
            KF_data[3] = beta_hat[0]

            if use_altitude_hold[0]:
                if not is_current_altitude_snap_shot_taken[0]:
                    current_altitude_snap_shot_mts[0] = distance__from_tof_sensor /1000
                    var_e_RC_mid_percentage[0] = rc.trimmer_VRE_percentage()
                    is_current_altitude_snap_shot_taken[0] = True
            else:
                is_current_altitude_snap_shot_taken[0] = False

        if use_altitude_hold[0] and not is_drone_flying_close_to_ground[0]:
            lqr.set_alpha_beta(alpha_hat[0], beta_hat[0])
            lqr.set_gains(-gain_kp_from_rc[0], -gain_kd_from_rc[0])
            throttle_ref_from_LQR[0] = lqr.control_action(np.array([[z_hat[0]], [v_hat[0]]]),
                                                          reference_altitude_mts=altitude_ref_mts[0],
                                                          recalculate_dynamics=True,
                                                          pitch_rad=euler[1],
                                                          roll_rad=euler[2])
            throttle_ref_from_LQR[0] = max(
                1000, min(throttle_ref_from_LQR[0]*900, 600) + 1000)
            Tref_t[0] = (throttle_ref_from_LQR[0] - 1000)/900
            print_debug(
                f"alphan hat: {alpha_hat[0]} beta hat: {beta_hat[0]} k11: {-gain_kp_from_rc[0]} k12: {-gain_kd_from_rc[0]} Tref_LQR: {Tref_t[0]} alt_hat: {z_hat[0]} alt_ref: {altitude_ref_mts[0]}")

    if enable_caching[0]:
        time_before_thread_starts[0] = time_ns()

    # schedule the necessary functions
    scheduler.schedule("process_radio_data",
                       process_radio_data,
                       function_call_frequency=50,
                       function_call_count=0)
    scheduler.schedule("process_ESP_data",
                       process_ESP_data,
                       function_call_frequency=50,
                       function_call_count=0)
    scheduler.schedule("read_ToF_run_kf_and_LQR",
                       read_ToF_run_kf_and_LQR,
                       function_call_frequency=sampling_frequency,
                       function_call_count=0)

    # THE MAIN LOOP
    EVO_filename = datetime.datetime.now().strftime("Evo-ToF-%d-%m-%y--%H-%M.csv")
    BAR_filename = datetime.datetime.now().strftime("PressureSensor-%d-%m-%y--%H-%M.csv")
    ANE_filename = datetime.datetime.now().strftime("Anemometer-%d-%m-%y--%H-%M.csv")
    GNSS_filename = datetime.datetime.now().strftime("GNSS-%d-%m-%y--%H-%M.csv")
    processor = AverageFilter()  # You need to define this class based on your requirements
    with (EvoSensor(window_length=3,  
                    data_processor=processor,  
                    log_file=EVO_filename) as ToFSensor, 
          PressureSensor(window_length=100,  
                         data_processor=processor,  
                         reference_pressure_at_sea_level=102500, 
                         log_file=BAR_filename) as PSensor, 
          Anemometer(window_length=5,  
                     data_processor=processor,  
                     log_file=ANE_filename) as ASensor,
          Gnss(window_length=3,  
                     data_processor=processor,  
                     log_file=GNSS_filename) as GnssSensor):
        
        while True:
            scheduler.run()  # run the scheduled functions

            if is_kill[0] and switch_a_status[0]:
                print("All sensors are saving data")
                break
    
    
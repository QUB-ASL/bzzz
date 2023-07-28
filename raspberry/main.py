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
from bzzz.estimators.altitude_Kalman_filter import KalmanFilter
from bzzz.controllers.altitude_LQR import LQR

if __name__ == '__main__':
    # sampling frequency of KF and LQR
    sampling_frequency = 50
    
    # objects declaration
    kf = KalmanFilter(sampling_frequency=sampling_frequency, initial_Tt=0, x_tilde_0=np.array([[0], [0], [10], [-9.81]]), P_0=np.diagflat([1, 1, 1, 0.01]), cache_values=True)
    lqr = LQR(sampling_frequency=sampling_frequency, initial_alpha_t=10, initial_beta_t=-9.81)
    tof = TimeOfFlightSensor(use_sleep=-1, num_latest_readings_to_keep=1, cache_altitude=True, use_outlier_detection=True, abs_outlier_diff_thres=500)
    rc = bzzz.read_sbus.RC()    
    scheduler = Scheduler(use_threading=False)

    # data caching and logging
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

    is_data_saved = [False]
    is_data_log_kill = [False]

    # Altitude hold vars
    throttle_ref_from_LQR = [0]
    use_altitude_hold = [False]
    Tref_t = [0.0]
    altitude_ref_mts = [0.09]
    current_altitude_snap_shot_mts = [0.0]
    is_current_altitude_snap_shot_taken = [False]
    var_e_RC_mid_percentage = [0.5]
    altitude_shifter_range_mts = [0.5]
    is_drone_flying_close_to_ground = [False]
    min_altitude_to_activate_AltiHold_mts = [0.15]
    is_KF_ran_atleast_once = [False]
    z_hat = [0.]
    v_hat = [0.]
    alpha_hat = [10.]
    beta_hat = [-9.81]

    _, plts = plt.subplots(4, 2)

    def rad2deg(lst):
        return [i*180/pi for i in lst]
    
    def euler_angles(q: list):
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

    def process_radio_data():
        if use_altitude_hold[0]:
            altitude_ref_mts[0] = current_altitude_snap_shot_mts[0] + (var_e_RC_mid_percentage[0] - rc.trimmer_VRE_percentage())*altitude_shifter_range_mts[0]
            print(f"Using altitude hold: Tref_LQR = {throttle_ref_from_LQR[0]}, {altitude_ref_mts}")
        channel_data = rc.get_radio_data_parse_and_send_to_ESP(return_channel_date=True, force_send_fake_data=False, fake_data="S,0,0,0,0,0,0,0,0,0", over_write_throttle_ref_to=throttle_ref_from_LQR[0][0][0] if use_altitude_hold[0] else -1)
        use_altitude_hold[0] = rc.switch_C() == True
        is_data_log_kill[0] = rc.switch_A() == True
        Tref_t[0] = (rc.throttle_reference_percentage() - 1000)/900
        throttle_ref_cache.append(Tref_t[0])


            
        # if rc.parser.kill():
            # altitude_cache_df = pd.DataFrame([[t, Tr, alt] for t, Tr, alt in zip(time_cache, throttle_ref_cache, tof.altitude_cache())])
            # altitude_cache_df.to_csv("/home/bzzz/Desktop/data_log.csv", index=False, header=False)
            # with open("/home/bzzz/Desktop/data_log.csv", "w") as file:
            #     file.write("time_stamps = %f,\n\n\n Throttle_reference = %f,\n\n\n altitude_cache = %f\n"%(time_cache, throttle_ref_cache, tof.altitude_cache()))
            # tof.kill_ToF()
            # altitude_logger_thread.cancel()
            # scheduler.kill("process_radio_data")
            # exit(0)

    def process_ESP_data():
        # process ESP data
        flight_data = rc.receive_data_from_ESP()
        if flight_data is not None and "FD:" in flight_data:
            flight_data = flight_data.strip().split()
            if len(flight_data) == 7:
                # try:
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
                if quat == [-1., -1., -1.]:
                    print(f"Received quat = {quat}. Defaulting to quat = [0, 0, 0].")
                    quat[0] = 0.
                    quat[1] = 0.
                    quat[2] = 0.
                q0 = sqrt(1 - quat[0]**2 - quat[1]**2 - quat[2]**2)
                full_quaternion = [q0] + quat
                euler[0], euler[1], euler[2] = euler_angles(full_quaternion)

                quat_cache.append(quat)
                yaw_cache.append(euler[0])
                pitch_cache.append(euler[1])
                roll_cache.append(euler[2])
                accelrometer_cache.append(acc[:])
                # except Exception as e:
                #     print("Exception in main.py: ", e)
                #     pass
    
    def read_ToF_run_kf_and_LQR():
        # NOTE: DO NOT DIVIDE temp BY 1000 here to get altitude measurements in mts. There are checks if temp == -1 in the code for outlier detection.
        # you can run LQR even when the drone is close to ground but you cannot run KF. So, to compensate use the previous estimates of alpha and beta
        # and the current ToF sensor readings. In this case if the ToF returns outliers send current altitude as desired altitude to LQR so it has no control.
        temp = tof.altitude
        is_drone_flying_close_to_ground[0] = temp/1000 < min_altitude_to_activate_AltiHold_mts[0]
        if is_drone_flying_close_to_ground[0]:
            z_hat[0] = current_altitude_snap_shot_mts[0] if temp == -1 else temp/1000
            print(f"Cannot activate Altitude hold. Drone is flying close to the ground at {temp/1000} mts < {min_altitude_to_activate_AltiHold_mts[0]} mts.")
        if use_altitude_hold[0] and not is_current_altitude_snap_shot_taken[0]:
            if not is_drone_flying_close_to_ground[0]:
                current_altitude_snap_shot_mts[0] = temp/1000
                var_e_RC_mid_percentage[0] = rc.trimmer_VRE_percentage()
                is_current_altitude_snap_shot_taken[0] = True

        if not use_altitude_hold[0]:
            is_current_altitude_snap_shot_taken[0] = False

        if not is_drone_flying_close_to_ground[0]:
            x_est = kf.run(Tref_t[0], euler[1], euler[2], np.nan if temp == -1 else temp/1000)
            is_KF_ran_atleast_once[0] = True
            z_hat[0] = x_est[0][0]
            v_hat[0] = x_est[1][0]
            alpha_hat[0] = x_est[2][0]
            beta_hat[0] = x_est[3][0]
        elif is_KF_ran_atleast_once[0]:
            kf.reset(0 if temp == -1 else temp, initial_Tt=Tref_t[0])
        
        if use_altitude_hold[0]:
            throttle_ref_from_LQR[0] = lqr.control_action(np.array([[z_hat[0]], [v_hat[0]]]), alpha_t=alpha_hat[0], beta_t=beta_hat[0], reference_altitude_mts=altitude_ref_mts[0], recalculate_dynamics=True, pitch_rad=euler[1], roll_rad=euler[2])                       
            throttle_ref_from_LQR[0] = min(1500, throttle_ref_from_LQR[0])
        if temp == -1:
            print("ToF outlier or -ve distance detected, discarded the measurement.")
        time_cache.append((time_ns() - time_before_thread_starts)/1000000)

    time_before_thread_starts = time_ns()
    scheduler.schedule("process_radio_data", process_radio_data, function_call_frequency=50, function_call_count=0)
    scheduler.schedule("process_ESP_data", process_ESP_data, function_call_frequency=50, function_call_count=0)
    scheduler.schedule("read_ToF_run_kf_and_LQR", read_ToF_run_kf_and_LQR, function_call_frequency=50, function_call_count=0)
    while True:
        scheduler.run()
        if not is_data_saved and is_data_log_kill[0]:
            print("saving data wait....")
            is_data_saved[0] = True
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
            # tof.kill_ToF()
            print("Saving done!")
            # break

    
    

# Run the get_radio_data_parse_and_send_to_ESP funtionn @ 50Hz
# run_thread_every_given_interval(0.02, get_radio_data_parse_and_send_to_ESP)
# run_thread_every_given_interval(0.02, print_receive_data_from_ESP)
# time_before_thread_starts = time_ns()
# bzzz.thread_this.run_thread_every_given_interval(0.02, run)

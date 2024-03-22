import numpy as np  # for matrix based calculations
import time
import datetime
import bzzz.util.constants as constants

from time import time_ns  # function to get system-up time in nano seconds
from bzzz.controllers.altitude_controller import *  # altitude hold controller
from bzzz.estimators.altitude_hold_kalman_filter import *
from bzzz.sensors.time_of_flight_sensor import TimeOfFlightSensor
from bzzz.read_sbus import RC
from bzzz.read_sbus.radioData import *
from bzzz.read_sbus.esp_bridge import *
from bzzz.sensors.evo_time_of_flight import EvoSensor
from bzzz.sensors.pressure_sensor import PressureSensor
from bzzz.sensors.anemometer import Anemometer
from bzzz.sensors.gnss import Gnss
from bzzz.sensors.data_logger import DataLogger
from bzzz.sensors.filters import *


if __name__ == '__main__':
    # Global variables
    params = constants.constants()
    min_altitude_hold_altitude = params["min_altitude_hold_altitude"]
    feature_names = ("datetime", "z_ref", "z", "z_hat",
                     "v_hat", "alpha_1", "alpha_0", "tau")
    logger = DataLogger(num_features=7,
                        feature_names=feature_names,
                        max_samples=50000)
    sampling_time = params["sampling_time"]
    kf_params = params["ah_kf"]
    altitude_kf = AltitudeHoldKalmanFilter(
        initial_state=np.array([1, 0, 20, -10]),
        initial_sigma=np.diagflat(kf_params["initial_sigma"]),
        state_cov=np.diagflat(kf_params["state_cov"]),
        meas_cov=kf_params["meas_cov"])
    altitude_ctrl = AltitudeController()
    rc = RC()

    class EmergencyMeasures(Enum):
        NO_PROBLEM = 0
        BELOW_HOVERING = 1
        ASSASSINATION = 2

    def emergency_measure(connection_lost,
                          radio_data,
                          tof):
        distance_from_ground = tof.distance
        kill_switch = radio_data.switch_D()
        if kill_switch or connection_lost:
            if np.isnan(distance_from_ground) \
                    or distance_from_ground < min_altitude_hold_altitude:
                return EmergencyMeasures.ASSASSINATION
            else:
                return EmergencyMeasures.BELOW_HOVERING
        return EmergencyMeasures.NO_PROBLEM

    def take_emergency_measure(measure, radio_data):
        match measure:
            case EmergencyMeasures.ASSASSINATION:
                radio_data.set_throttle(300)
            case EmergencyMeasures.BELOW_HOVERING:
                radio_data.set_throttle(800)
                radio_data.set_switch_D(True)

    def trimmer_to_altitude_increment(val):
        if val >= 0.35 and val <= 0.65:
            return 0
        if val > 0.65:
            return (val - 0.65)/0.35
        if val < 0.35:
            return (val - 0.35)/0.35
        return 0

    def altitude_estimator(radio_data, y):
        tau = radio_data.throttle_reference_percentage()
        altitude_kf.update(tau, 0, 0, y)

    def percentage_to_throttle_radio(val):
        return 300 + 1400 * val

    def altitude_control(radio_data):
        vre = radio_data.trimmer_VRE_percentage()
        sc_vre = trimmer_to_altitude_increment(vre)
        cm_pre_sec_max_increment = 0.02
        cm_pre_tick_max_increment = cm_pre_sec_max_increment * sampling_time
        increment_action = sc_vre * cm_pre_tick_max_increment
        altitude_ctrl.increment_reference(increment_action)
        altitude_ctrl.set_tau_eq(altitude_kf.tau_eq_estimate())
        altitude_ctrl.set_p_gain(-radio_data.trimmer_VRA_percentage() * 3)
        altitude_ctrl.set_d_gain(-radio_data.trimmer_VRB_percentage() * 0.05)
        state_est = altitude_kf.x_measured()
        tau = altitude_ctrl.control_action(state_est[0], state_est[1])
        print(state_est[0], state_est[1], state_est[2],
              state_est[3], altitude_kf.tau_eq_estimate(), tau)
        clip_throttle = percentage_to_throttle_radio(0.5)
        throttle = int(
            min(percentage_to_throttle_radio(tau)[0], clip_throttle))
        radio_data.set_throttle(throttle)

    def save_data():
        blackbox_fname = datetime.datetime.now().strftime("BB-%d-%m-%y--%H-%M.csv")
        logger.save_to_csv(blackbox_fname)
        print("All sensors are saving data; bye!")

    def record_black_box_data(radio_data, y):
        current_timestamp = datetime.datetime.now()
        state_est = altitude_kf.x_measured()
        data_to_log = np.zeros((7, ))
        data_to_log[0] = y
        data_to_log[1] = altitude_ctrl.altitude_reference()
        data_to_log[2:6] = state_est.reshape((4, ))
        data_to_log[6] = radio_data.throttle_reference_percentage()
        logger.record(current_timestamp, data_to_log)

    def control_loop(tof, bar, gps, esp_bridge):
        connection_lost_flag, radio_data = rc.get_radio_data()
        radio_data = RadioData(radio_data)
        do_kill = radio_data.switch_D()
        do_save = radio_data.switch_A()

        if do_kill and do_save:
            save_data()
            return False

        measure = emergency_measure(connection_lost_flag,
                                    radio_data,
                                    tof)
        take_emergency_measure(measure, radio_data)

        flight_mode = radio_data.switch_C()
        y_tof = tof.distance
        y_bar = ...
        y_gps = ...
        y = np.array([y_tof, y_bar, y_gps])
        
        if y > min_altitude_hold_altitude:
            altitude_estimator(radio_data, y)  # deals with nans

        match flight_mode:
            case ThreeWaySwitch.MID.value:
                if y > min_altitude_hold_altitude:
                    altitude_control(radio_data)
            case _:
                altitude_ctrl.set_altitude_reference(tof.distance)

        esp_bridge.send_to_esp(radio_data)
        record_black_box_data(radio_data, y)
        return True

    # ------------------------------------------------
    # MAIN LOOP!
    # ------------------------------------------------
    keep_running = True
    with (EvoSensor(data_processor=MedianFilter()) as tof,
          Barometer as barom
          Gnss(data_processor=MedianFilter()) as gps,
          EspBridge() as esp_bridge):
        starttime = time_ns()
        while keep_running:
            keep_running = control_loop(tof, bar, gps, esp_bridge)
            time.sleep(0.018)

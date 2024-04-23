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
from bzzz.sensors.pressure_sensor import BMP180Sensor
from bzzz.sensors.anemometer import Anemometer
from bzzz.sensors.gnss import Gnss
from bzzz.sensors.data_logger import DataLogger
from bzzz.sensors.filters import *

from bzzz.estimators.altitude_kalman_filter_2 import *

if __name__ == '__main__':
    # Global variables
    params = constants.constants()
    min_altitude_hold_altitude = params["min_altitude_hold_altitude"]
    feature_names = ("datetime", "z_tof", "z_bar", "z_ref", "z_hat",
                     "v_hat", "alpha_1", "alpha_0", "tau", "z_hat_2",
                     "v_hat_2", "alpha_1_2", "alpha_0_2", "d_bar")
    logger = DataLogger(num_features=13,
                        feature_names=feature_names,
                        max_samples=50000)
    sampling_time = params["sampling_time"]
    kf_params = params["ah_kf"]
    altitude_kf = AltitudeHoldKalmanFilter(
        initial_state=np.array(kf_params["initial_state"]),
        initial_sigma=np.diagflat(kf_params["initial_sigma"]),
        state_cov=np.diagflat(kf_params["state_cov"]),
        meas_cov=kf_params["meas_cov"])
    altitude_ctrl = AltitudeController()
    rc = RC()

    altitude_kf_est_2 = AltitudeKalmanFilter2(
        initial_state=np.array(kf_params["initial_state_2"]),
        initial_sigma=np.diagflat(kf_params["initial_sigma_2"]),
        state_cov=np.diagflat(kf_params["state_cov_2"]),
        meas_cov=kf_params["meas_cov_2"])

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

    def altitude_estimator2(radio_data, y):
        tau = radio_data.throttle_reference_percentage()
        altitude_kf_est_2.update(tau, 0, 0, y)

    def percentage_to_throttle_radio(val):
        return 300 + 1400 * val

    def altitude_control(radio_data):
        vre = radio_data.trimmer_VRE_percentage()
        sc_vre = trimmer_to_altitude_increment(vre)
        meters_pre_sec_max_increment = 0.04
        meters_pre_tick_max_increment = meters_pre_sec_max_increment * sampling_time
        increment_action = sc_vre * meters_pre_tick_max_increment
        altitude_ctrl.increment_reference(increment_action)
        altitude_ctrl.set_tau_eq(altitude_kf.tau_eq_estimate())
        altitude_ctrl.set_p_gain(-radio_data.trimmer_VRA_percentage() * 2)
        altitude_ctrl.set_d_gain(-radio_data.trimmer_VRB_percentage() * 1)
        state_est = altitude_kf.x_measured()
        tau = altitude_ctrl.control_action(state_est[0], state_est[1])
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
        state_est_2 = altitude_kf_est_2.x_measured()
        data_to_log = np.zeros((13, ))
        data_to_log[0] = y[0]
        data_to_log[1] = y[1]
        data_to_log[2] = altitude_ctrl.altitude_reference()
        data_to_log[3:7] = state_est.reshape((4, ))
        data_to_log[7] = radio_data.throttle_reference_percentage()
        data_to_log[8:13] = state_est_2.reshape((5, ))
        logger.record(current_timestamp, data_to_log)

    def control_loop(tof, barometer, esp_bridge):
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
        y_bar = barometer.altitude()
        y = np.array([y_tof, y_bar])
        if y_tof > min_altitude_hold_altitude:
            altitude_estimator(radio_data, y_tof)  # deals with nans
            altitude_estimator2(radio_data, y)

        match flight_mode:
            case ThreeWaySwitch.MID.value:
                if y_tof > min_altitude_hold_altitude:
                    altitude_control(radio_data)
            case _:
                altitude_ctrl.set_altitude_reference(tof.distance)

        esp_bridge.send_to_esp(radio_data)
        record_black_box_data(radio_data, y)
        return True

    # ------------------------------------------------
    # MAIN LOOP!
    # ------------------------------------------------
    EVO_filename = datetime.datetime.now().strftime("Evo-ToF-%d-%m-%y--%H-%M.csv")
    BAR_filename = datetime.datetime.now().strftime("PressureSensor-%d-%m-%y--%H-%M.csv")
    ANE_filename = datetime.datetime.now().strftime("Anemometer-%d-%m-%y--%H-%M.csv")
    GNSS_filename = datetime.datetime.now().strftime("GNSS-%d-%m-%y--%H-%M.csv")
    processor = MedianFilter()  # You need to define this class based on your requirements
    keep_running = True
    with (EvoSensor(window_length=3,  
                    data_processor=processor,  
                    log_file=EVO_filename) as tof, 
          Anemometer(log_file=ANE_filename) as anemometer,
          BMP180Sensor(log_file=BAR_filename) as barometer,
        #   Gnss(log_file=GNSS_filename) as gnss,
          EspBridge() as esp_bridge):
        starttime = time_ns()
        while keep_running:
            keep_running = control_loop(tof, barometer, esp_bridge)
            time.sleep(0.018)

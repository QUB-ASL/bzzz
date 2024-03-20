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
    # sampling frequency of KF and LQR
    sampling_frequency = 50
    # caching configuration
    enable_caching = [True]
    enable_printing_cache_to_screen = [False and enable_caching[0]]

    params = constants.constants()

    # objects declaration
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
                           tof,
                           min_critical_altitude = 0.6):
        #TODO (important) radio_data could be None; the ESP deals with cases where no data is sent
        distance_from_ground = tof.distance       
        kill_switch = radio_data.switch_D()
        if kill_switch or connection_lost:
            if np.isnan(distance_from_ground) \
                    or distance_from_ground < min_critical_altitude:
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

    MIN_ALTITUDE_HOLD_ALTITUDE = 0.6

    def trimmer_to_altitude_increment(val):
        if val >= 0.35 and val <= 0.65:
            return 0
        if val > 0.65:
            return (val - 0.65)/0.35
        if val < 0.35:
            return (val - 0.35)/0.35
        return 0

    def altitude_estimator(radio_data, tof):
        y = tof.distance
        if y < MIN_ALTITUDE_HOLD_ALTITUDE:
            return
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
        altitude_ctrl.set_d_gain(-radio_data.trimmer_VRB_percentage() * 2)
        state_est = altitude_kf.x_measured()
        tau = altitude_ctrl.control_action(state_est[0], state_est[1])
        clip_throttle = percentage_to_throttle_radio(0.5)
        throttle = int(min(percentage_to_throttle_radio(tau), clip_throttle)[0])
        radio_data.set_throttle(throttle)
        

    def control_loop(tof, esp_bridge):
        keep_running = True
        connection_lost_flag, radio_data = rc.get_radio_data()
        
        radio_data = RadioData(radio_data)
        measure = emergency_measure(connection_lost_flag,
                                    radio_data,
                                    tof)
        take_emergency_measure(measure, radio_data)

        flight_mode = radio_data.switch_C()

        if tof.distance > 0.6:
            altitude_estimator(radio_data, tof)
        
        match flight_mode:
            case ThreeWaySwitch.MID.value:
                altitude_control(radio_data)
            case other:
                altitude_ctrl.set_altitude_reference(tof.distance)

        esp_bridge.send_to_esp(radio_data)
        return keep_running

    # ------------------------------------------------
    # MAIN LOOP!
    # ------------------------------------------------
    keep_running = True
    evo_filename = datetime.datetime.now().strftime("Evo-%d-%m-%y--%H-%M.csv")
    with (EvoSensor(log_file=evo_filename) as tof,
          EspBridge() as esp_bridge):
        starttime = time_ns()
        while keep_running:
            # elapsed_time = time_ns() - starttime
            # print(elapsed_time/1000)
            keep_running = control_loop(tof, esp_bridge)
            time.sleep(0.018)

    # # THE MAIN LOOP
    # EVO_filename = datetime.datetime.now().strftime("Evo-ToF-%d-%m-%y--%H-%M.csv")
    # BAR_filename = datetime.datetime.now().strftime("PressureSensor-%d-%m-%y--%H-%M.csv")
    # ANE_filename = datetime.datetime.now().strftime("Anemometer-%d-%m-%y--%H-%M.csv")
    # GNSS_filename = datetime.datetime.now().strftime("GNSS-%d-%m-%y--%H-%M.csv")
    # processor = AverageFilter()  # You need to define this class based on your requirements
    # with (EvoSensor(window_length=3,
    #                 data_processor=processor,
    #                 log_file=EVO_filename) as tof,
    #       PressureSensor(window_length=100,
    #                      data_processor=processor,
    #                      reference_pressure_at_sea_level=102500,
    #                      log_file=BAR_filename) as PSensor,
    #       Anemometer(window_length=5,
    #                  data_processor=processor,
    #                  log_file=ANE_filename) as ASensor,
    #       Gnss(window_length=3,
    #                  data_processor=processor,
    #                  log_file=GNSS_filename) as GnssSensor):

    #     while True:
    #         scheduler.run()  # run the scheduled functions

    #         if is_kill[0] and switch_a_status[0]:
    #             print("All sensors are saving data")
    #             break

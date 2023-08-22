# TODO: REFINE THIS CODE
# NOTE: THIS IS FOR FUTURE PURPOSES, CURRENTLY IT HAS NO USAGE

from sensors.pressure_sensor import PressureSensor as PS
from sensors.time_of_flight_sensor import TimeOfFlightSensor as ToF
# from standard_controllers import PD_controller
from altitude_LQR import LQR

class AltitudeHoldController:
    def __init__(self, update_frequency, initial_alpha_t, initial_beta_t):
        self.pressure_sensor = PS(median_filter_length=5)
        self.time_of_flight_sensor = ToF(median_filter_length=5)
        self.update_frequency = update_frequency
        self.sampling_time = 1/self.update_frequency
        
        self._LQR = LQR(sampling_frequency=update_frequency, initial_alpha_t=initial_alpha_t, initial_beta_t=initial_beta_t)

        self._current_altitude = None
        self._previous_altitude = None
        self._altitude_dot = None  # rate of change of altitude, first derivative of altitude.

        self._calculated_upward_thrust = None

    def _update_altitude(self):
        # TODO: do sensor fusion
        # NOTE: usually ToF has faster update rate (at least 50Hz) and least error (max 6cm), 
        # but have shorter range and readings are error prone based on surface reflectance and angle of incidence (attitude dependent).
        # NOTE: whereas pressure sensors are slow (max 20Hz) and large error (min 17cm, max 50cm),
        # but are more reliable, have long range (works upto 100Km above sea-level), independent of attitude.
        # NOTE: Take altitude readings from both sensors and compare, if ToF is far off from pressure sensor, 
        # discard ToF readings as pressure sensor is more reliable. This check also covers the case for attitude related problems.
        # NOTE: use multi-threadding to read sensors at specific rates (usually ToF@50Hz and pressure sensor@20Hz)
        # NOTE: if the surface has different reflectance and this is the only issue, slowly increase height and 
        # see if altitude reading from ToF increases linearly. If so, you can find an affine transformation that gives the correct reading.
        # This is particularly helpful as we can now have the higher refresh rate of ToF.
        # NOTE: FOR NOW WE ARE JUST AVERAGING THE SENSORS' ALTITUDE READINGS. IMPLEMENT PROPER CODE LATER
        p_sen_altitude = self.pressure_sensor.altitude
        ToF_altitude = self.time_of_flight_sensor.altitude

        true_altitude = (p_sen_altitude + ToF_altitude)/2
        # TODO: CHECK IF true_altitude IS A PROPER VALUE
        # IF YES UPDATE BELOW ELSE RETURN
        self._previous_altitude = self._current_altitude
        self._current_altitude = true_altitude
        self._altitude_dot = (self._current_altitude - self._previous_altitude)/self.sampling_time

    @property
    def thrust(self):
        return self._calculated_upward_thrust
    
    def get_control_action_thrust(self, current_states_z_and_vz, alpha_t=1, beta_t=-9.81, reference_altitude_mts=1, recalculate_dynamics=True):
        control_action_thrust = LQR.control_action(current_states_z_and_vz=current_states_z_and_vz, alpha_t=alpha_t, beta_t=beta_t,
                                                    reference_altitude_mts=reference_altitude_mts, recalculate_dynamics=recalculate_dynamics)
        return control_action_thrust




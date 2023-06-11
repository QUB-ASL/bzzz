# TODO: Change all of the list vars into numpy arrays in all the files

from math import sqrt

from parts.arm import Arm
from parts.battery import Battery
from parts.BLDCM import BLDC
from parts.casing_with_electronics import CasingWithElectronics
from parts.ESC import ESC
from parts.propeller import Propeller


FRONT_RIGHT_MOTOR = 'front right motor'
FRONT_LEFT_MOTOR = 'front left motor'
BACK_LEFT_MOTOR = 'back left motor'
BACK_RIGHT_MOTOR = 'back right motor'

MOTOR_RPM = 'RPM'
MOTOR_I_RMS_AMP = 'iRMS'
MOTOR_TORQUE_N_MTS = 'torque'



class QuadCopter:
    def __init__(self) -> None:
        self.__simulation_time_step_sec = None

        self.__arms = {
            FRONT_RIGHT_MOTOR: Arm(),
              FRONT_LEFT_MOTOR: Arm(),
                BACK_LEFT_MOTOR: Arm(),
                  BACK_RIGHT_MOTOR: Arm()}
        self.__battery = Battery()
        self.__BLDCs = {
            FRONT_RIGHT_MOTOR: BLDC(),
              FRONT_LEFT_MOTOR: BLDC(),
                BACK_LEFT_MOTOR: BLDC(),
                  BACK_RIGHT_MOTOR: BLDC()}
        self.__casing_with_electronics = CasingWithElectronics()
        self.__ESCs = {
            FRONT_RIGHT_MOTOR: ESC(),
             FRONT_LEFT_MOTOR: ESC(),
              BACK_LEFT_MOTOR: ESC(),
               BACK_RIGHT_MOTOR: ESC()}
        self.__propellers = {
            FRONT_RIGHT_MOTOR: Propeller(),
             FRONT_LEFT_MOTOR: Propeller(), 
              BACK_LEFT_MOTOR: Propeller(),
               BACK_RIGHT_MOTOR: Propeller()}
        self.__BLDCs_simulation_params = {
            FRONT_RIGHT_MOTOR: {MOTOR_RPM: 0, MOTOR_TORQUE_N_MTS: 0, MOTOR_I_RMS_AMP: 0},
             FRONT_LEFT_MOTOR: {MOTOR_RPM: 0, MOTOR_TORQUE_N_MTS: 0, MOTOR_I_RMS_AMP: 0}, 
              BACK_LEFT_MOTOR: {MOTOR_RPM: 0, MOTOR_TORQUE_N_MTS: 0, MOTOR_I_RMS_AMP: 0},
               BACK_RIGHT_MOTOR: {MOTOR_RPM: 0, MOTOR_TORQUE_N_MTS: 0, MOTOR_I_RMS_AMP: 0}}
        
        self.__total_current_drawn_RMS_amp = None

        self.__is_first_run = True

    def __compute_VRMSs_from_PWM_ESCs(self, front_right_motor_PWM_percentile, front_left_motor_PWM_percentile, back_left_motor_PWM_percentile, back_right_motor_PWM_percentile):
        front_right_motor_VRMS_percentile = self.__ESCs[FRONT_RIGHT_MOTOR].simulate(front_right_motor_PWM_percentile)
        front_left_motor_VRMS_percentile = self.__ESCs[FRONT_LEFT_MOTOR].simulate(front_left_motor_PWM_percentile)
        back_left_motor_VRMS_percentile = self.__ESCs[BACK_LEFT_MOTOR].simulate(back_left_motor_PWM_percentile)
        back_right_motor_VRMS_percentile = self.__ESCs[BACK_RIGHT_MOTOR].simulate(back_right_motor_PWM_percentile)
        return front_right_motor_VRMS_percentile, front_left_motor_VRMS_percentile, back_left_motor_VRMS_percentile, back_right_motor_VRMS_percentile

    def __simulate_BLDCs(self, *FR_FL_BL_BR_VRMSs):
        FR_VRMS, FL_VRMS, BL_VRMS, BR_VRMS = FR_FL_BL_BR_VRMSs
        
        self.__BLDCs_simulation_params[FRONT_RIGHT_MOTOR][MOTOR_RPM], 
        self.__BLDCs_simulation_params[FRONT_RIGHT_MOTOR][MOTOR_TORQUE_N_MTS],
        self.__BLDCs_simulation_params[FRONT_RIGHT_MOTOR][MOTOR_I_RMS_AMP] = self.__BLDCs[FRONT_RIGHT_MOTOR].simulate(FR_VRMS)
        
        self.__BLDCs_simulation_params[FRONT_LEFT_MOTOR][MOTOR_RPM], 
        self.__BLDCs_simulation_params[FRONT_LEFT_MOTOR][MOTOR_TORQUE_N_MTS],
        self.__BLDCs_simulation_params[FRONT_LEFT_MOTOR][MOTOR_I_RMS_AMP] = self.__BLDCs[FRONT_LEFT_MOTOR].simulate(FL_VRMS)
        
        self.__BLDCs_simulation_params[BACK_LEFT_MOTOR][MOTOR_RPM], 
        self.__BLDCs_simulation_params[BACK_LEFT_MOTOR][MOTOR_TORQUE_N_MTS],
        self.__BLDCs_simulation_params[BACK_LEFT_MOTOR][MOTOR_I_RMS_AMP] = self.__BLDCs[BACK_LEFT_MOTOR].simulate(BL_VRMS)
        
        self.__BLDCs_simulation_params[BACK_RIGHT_MOTOR][MOTOR_RPM], 
        self.__BLDCs_simulation_params[BACK_RIGHT_MOTOR][MOTOR_TORQUE_N_MTS],
        self.__BLDCs_simulation_params[BACK_RIGHT_MOTOR][MOTOR_I_RMS_AMP] = self.__BLDCs[BACK_RIGHT_MOTOR].simulate(BR_VRMS)

        self.__total_current_drawn_RMS_amp = self.__BLDCs_simulation_params[FRONT_RIGHT_MOTOR][MOTOR_I_RMS_AMP] + self.__BLDCs_simulation_params[FRONT_LEFT_MOTOR][MOTOR_I_RMS_AMP] + self.__BLDCs_simulation_params[BACK_LEFT_MOTOR][MOTOR_I_RMS_AMP] + self.__BLDCs_simulation_params[BACK_RIGHT_MOTOR][MOTOR_I_RMS_AMP]

    def __is__ESCs_current_overload(self):
        FR_ESC = self.__ESCs[FRONT_RIGHT_MOTOR].is_current_overload(self.__BLDCs_simulation_params[FRONT_RIGHT_MOTOR][MOTOR_I_RMS_AMP])
        FL_ESC = self.__ESCs[FRONT_LEFT_MOTOR].is_current_overload(self.__BLDCs_simulation_params[FRONT_LEFT_MOTOR][MOTOR_I_RMS_AMP])
        BL_ESC = self.__ESCs[BACK_LEFT_MOTOR].is_current_overload(self.__BLDCs_simulation_params[BACK_LEFT_MOTOR][MOTOR_I_RMS_AMP])
        BR_ESC = self.__ESCs[BACK_RIGHT_MOTOR].is_current_overload(self.__BLDCs_simulation_params[BACK_RIGHT_MOTOR][MOTOR_I_RMS_AMP])
        
        if FR_ESC:
            Exception("Front right ESC current overload \n  max ESC current: %f \n  Current demand: %f "
                      %(self.__ESCs[FRONT_RIGHT_MOTOR].max_amperage(), self.__BLDCs_simulation_params[FRONT_RIGHT_MOTOR][MOTOR_I_RMS_AMP]))
    
        if FL_ESC:
            Exception("Front left ESC current overload \n  max ESC current: %f \n  Current demand: %f "
                      %(self.__ESCs[FRONT_LEFT_MOTOR].max_amperage(), self.__BLDCs_simulation_params[FRONT_LEFT_MOTOR][MOTOR_I_RMS_AMP]))
    
        if BL_ESC:
            Exception("Back left ESC current overload \n  max ESC current: %f \n  Current demand: %f "
                      %(self.__ESCs[BACK_LEFT_MOTOR].max_amperage(), self.__BLDCs_simulation_params[BACK_LEFT_MOTOR][MOTOR_I_RMS_AMP]))
    
        if BR_ESC:
            Exception("Back right ESC current overload \n  max ESC current: %f \n  Current demand: %f "
                      %(self.__ESCs[BACK_RIGHT_MOTOR].max_amperage(), self.__BLDCs_simulation_params[BACK_RIGHT_MOTOR][MOTOR_I_RMS_AMP]))
    
    
    def __is__battery_current_overload(self):
        peak_current_drawn_amp = self.__total_current_drawn_RMS_amp*sqrt(2)
        battery_iLD = self.__battery.is_current_overload(peak_current_drawn_amp)
        
        if battery_iLD:
            Exception("Battery current overload \n  max battery current: %f \n  peak current demand: %f "
                      %(self.__battery.__max_output_current_amp(), peak_current_drawn_amp))
    

    def simulate(self, *FR_FL_BL_BR_PWMs_percentile):
        FR_FL_BL_BR_VRMSs = None
        if self.__is_first_run:
            FR_FL_BL_BR_VRMSs_percentile = self.__compute_VRMSs_from_PWM_ESCs(*FR_FL_BL_BR_PWMs_percentile)
            current_battery_voltage = self.__battery.current_EMF()
            FR_FL_BL_BR_VRMSs = current_battery_voltage*FR_FL_BL_BR_VRMSs_percentile
            self.__is_first_run = False
            
        self.__simulate_BLDCs(*FR_FL_BL_BR_VRMSs)

        self.__is__ESCs_current_overload()
        self.__is__battery_current_overload()

        self.__battery.simulate(self.__total_current_drawn_RMS_amp, self.__simulation_time_step_sec)



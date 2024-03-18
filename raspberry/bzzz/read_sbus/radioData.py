from enum import Enum

# Maximum pitch value corresponding to the top position of the stick (30deg = 0.52rad)
PITCH_MAX_RAD = 0.5235987755982988

# Value from the radio when the stick is at the lowest position
RADIO_STICK_MIN = 300

# Value from the radio when the stick is at the highest position
RADIO_STICK_MAX = 1700

# Maximum yaw rate (rad/s) 10 deg/s = 0.1745 rad/s
RADIO_MAX_YAW_RATE_RAD_SEC = 0.1745*300



# Radio data channels
RADIO_CHANNEL_YAW_RATE = 0
RADIO_CHANNEL_PITCH = 1
RADIO_CHANNEL_THROTTLE = 2
RADIO_CHANNEL_ROLL = 3
RADIO_CHANNEL_VRA = 5
RADIO_CHANNEL_VRB = 7
RADIO_CHANNEL_VRC = 6
RADIO_CHANNEL_VRE = 11
RADIO_CHANNEL_SWITCH_A = 9
RADIO_CHANNEL_SWITCH_B = 8
RADIO_CHANNEL_SWITCH_C = 4
RADIO_CHANNEL_SWITCH_D = 10

# Enum for three-way switches
class ThreeWaySwitch(Enum):
    """Enum for three-way switches

    :param Enum: Of parent class Enum
    """
    DOWN = 0
    MID = 1
    UP = 2


# Min and Max PWMs for rotor speed
ZERO_ROTOR_SPEED = 1000
ABSOLUTE_MAX_PWM = 1900




class RadioData:
    """RadioDataParser Class provides functions that help 
    in processing and encoding radio data.
    """
    def __init__(self, raw_channel_data=None):
        """Constructor
        """
        if raw_channel_data is not None:
            self.m_channelData = list(map(lambda x: 0 if int(x) < 0 else (
                2000 if int(x) > 2000 else int(x)), raw_channel_data.strip().split(",")))
        self.rawRatePercentage = None
        self.switchValue = None


    def __map_radio_to_angle(self, x, stick_min=RADIO_STICK_MIN, stick_max=RADIO_STICK_MAX):
        """Maps radio stick positions to corresponding angles in radians linearly.

        :param x: Stick position data.
        :param stick_min: Minimum value of radio stick, defaults to RADIO_STICK_MIN
        :param stick_max: Maximum value of radio stick, defaults to RADIO_STICK_MAX
        :return: angle in radians.
        """
        return -PITCH_MAX_RAD + (x - stick_min) / (stick_max - stick_min) * 2 * PITCH_MAX_RAD

    def __map_trimmer_to_percentage(self, x, stick_min = RADIO_STICK_MIN, stick_max = RADIO_STICK_MAX):
        """Linearly maps radio timmer or stick data to percentage [0, 1].

        :param x: Stick or trimmer position data.
        :param stick_min: Minimum value of radio stick, defaults to RADIO_STICK_MIN
        :param stick_max: Maximum value of radio stick, defaults to RADIO_STICK_MAX
        :return: Percentage in range [0, 1].
        """
        percentage = (x - stick_min) / (stick_max - stick_min)
        return max(min(percentage, 1), 0)

    def pitch_reference_angle_rad(self):
        """Maps pitch stick data to reference pitch angle in radians.

        :return: reference pitch angle in radians.
        """
        return self.__map_radio_to_angle(self.m_channelData[RADIO_CHANNEL_PITCH])

    def roll_reference_angle_rad(self):
        """Maps roll stick data to reference roll angle in radians.

        :return: reference roll angle in radians.
        """
        return self.__map_radio_to_angle(self.m_channelData[RADIO_CHANNEL_ROLL])

    def yaw_rate_reference_rad_sec(self):
        """Maps yaw stick data to reference yaw angle in radians.

        :return: reference yaw angle in radians.
        """
        self.rawRatePercentage = self.__map_trimmer_to_percentage(self.m_channelData[RADIO_CHANNEL_YAW_RATE])
        return -RADIO_MAX_YAW_RATE_RAD_SEC + 2 * RADIO_MAX_YAW_RATE_RAD_SEC * self.rawRatePercentage
    
    def throttle_reference_percentage(self):
        """Maps throttle stick data to reference percentage.

        :return: percentage reference of throttle.
        """
        return self.__map_trimmer_to_percentage(
            self.m_channelData[RADIO_CHANNEL_THROTTLE])

    def switch_B(self):
        """Checks if switch B has been toggled.

        :return: switch B status. True if On else False.
        """
        return self.m_channelData[RADIO_CHANNEL_SWITCH_B] >= 1500

    def switch_A(self):
        """Checks if switch A has been toggled.

        :return: switch A status. True if On else False.
        """
        return self.m_channelData[RADIO_CHANNEL_SWITCH_A] >= 1500

    def switch_C(self):
        """Checks the position of the three-way switch C.

        :return: Three-way switch position. DOWN = 0, MID = 1, UP = 2.
        """
        self.switchValue = self.m_channelData[RADIO_CHANNEL_SWITCH_C]
        if self.switchValue <= 450:
            return ThreeWaySwitch.DOWN.value
        elif self.switchValue <= 1200:
            return ThreeWaySwitch.MID.value
        return ThreeWaySwitch.UP.value

    def switch_D(self):
        """Checks the positon of the switch D.

        :return: Switch D position.
        """
        return self.m_channelData[RADIO_CHANNEL_SWITCH_D] >= 1500

    def trimmer_VRA_percentage(self):
        """Maps Variable Resistor A data to percentage.

        :return: VRA percentage in range [0, 1].
        """
        return self.__map_trimmer_to_percentage(self.m_channelData[RADIO_CHANNEL_VRA])

    def trimmer_VRC_percentage(self):
        """Maps Variable Resistor C data to percentage.

        :return: VRC percentage in range [0, 1].
        """
        return self.__map_trimmer_to_percentage(self.m_channelData[RADIO_CHANNEL_VRC])

    def trimmer_VRB_percentage(self):
        """Maps Variable Resistor B data to percentage.

        :return: VRB percentage in range [0, 1].
        """
        return self.__map_trimmer_to_percentage(self.m_channelData[RADIO_CHANNEL_VRB])

    def trimmer_VRE_percentage(self):
        """Maps Variable Resistor E data to percentage.

        :return: VRE percentage in range [0, 1].
        """
        return self.__map_trimmer_to_percentage(self.m_channelData[RADIO_CHANNEL_VRE])
    
    def __map_prcnt(self, percentage, minVal, maxVal):
        """Linearly maps percentage data to range [minVal, maxVal].

        :param percentage: Value of percentage, in range [0, 1], to be mapped.
        :param minVal: Lower boundary of the mapped data.
        :param maxVal: Upper boundary of the mapped data.
        :return: mapped data in range [minVal, maxVal].
        """
        return minVal + percentage * (maxVal - minVal)
    
    def set_throttle(self, throttle):
        self.m_channelData[RADIO_CHANNEL_THROTTLE] = throttle
    
    def set_switch_D(self, switch_value=True):
        # True = Kill = Down
        self.m_channelData[10] =  1000 if switch_value else 1600

    def format_radio_data_for_sending(self):
        """Processes, encodes, and formats the radio data into a 
        string so that it can be sent via UART.

        The formatted data has the following structure:
        
        ```
        S, Y, P, R, T, VRA, VRB, VRC, VRE, SWTCHs
        ```

        where:
        - `S` is the packet start indicator, 
        - `Y` is yaw reference rate in rad/s,
        - `P` is pitch reference angle in rad,
        - `R` is roll reference angle in rad,
        - `T` is PWM signal according to given throttle percentage,
        - `VRA` is percentage trimmer A value,
        - `VRB` is percentage trimmer B value,
        - `VRC` is percentage trimmer C value,
        - `VRE` is percentage trimmer E value,
        - `SWTCHs` is an integer whose last five bits contain the encoded position data of 
           the A, B, C, and D switches, and the encoding is as follows:
            
            ```
            |0|0|0|B|A|C|c|D| 
            ```
            
            this is the Least-significant byte of the sent integer in which
            
            - bit `|B|` indicates switch B's position 
            - bit `|A|` indicates switch A's position 
            - bits `|C|c|` together indicate switch C's position
            - bit `|D|` indicates switch D's position  

            For switches `A`, `B`, and `D` (since these are only two-way switches), each 
            were assigned a single bit with 0 indicating that the switch is in off state
            and 1 otherwise. For switch C, as it is a three-way switch, it was assigned with
            two bits with 00 = DOWN, 01 = MID, and 10 = UP.    
        
        :return: Formatted string that contains the processed radio data, 
                 where each data point is seperated by a comma.
        """
        reArrangedYPRTData = [
            self.yaw_rate_reference_rad_sec(), 
            self.pitch_reference_angle_rad(), 
            self.roll_reference_angle_rad(), 
            self.__map_prcnt(self.throttle_reference_percentage(), 
                             ZERO_ROTOR_SPEED, 
                             ABSOLUTE_MAX_PWM)]
        bitEncodedSwithcesData = (
            self.switch_B() << 4) \
        | (self.switch_A() << 3) \
        | (self.switch_C() << 1) \
        | self.switch_D()
        reArrangedABCETrimmersData = [
            self.trimmer_VRA_percentage(), 
            self.trimmer_VRB_percentage(), 
            self.trimmer_VRC_percentage(), 
            self.trimmer_VRE_percentage()]

        reArrangedData = reArrangedYPRTData + reArrangedABCETrimmersData
        
        return reArrangedData + [bitEncodedSwithcesData], ",".join(map(lambda x: str(x)[:5], reArrangedData)) + f",{bitEncodedSwithcesData}"

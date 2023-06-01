from enum import Enum

# Maximum pitch value corresponding to the top position of the stick (30deg = 0.52rad)
PITCH_MAX_RAD = 0.5235987755982988

# Value from the radio when the stick is at the lowest position
RADIO_STICK_MIN = 300

# Value from the radio when the stick is at the highest position
RADIO_STICK_MAX = 1700

# Maximum yaw rate (rad/s) 10 deg/s = 0.1745 rad/s
RADIO_MAX_YAW_RATE_RAD_SEC = 0.1745

# Trimmer A on RC - maximum quaternion XY gain
RADIO_TRIMMER_MAX_QUATERNION_XY_GAIN = 100.

# Trimmer B on RC - maximum quaternion Z gain
RADIO_TRIMMER_MAX_QUATERNION_Z_GAIN = 20.

# Trimmer C on RC - maximum omega xy gain
RADIO_TRIMMER_MAX_OMEGA_XY_GAIN = 0.5

# Trimmer E on RC - maximum omega z gain
RADIO_TRIMMER_MAX_OMEGA_Z_GAIN = 0.05

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

    :param Enum: Parent class
    :type Enum: Enumerator
    """
    DOWN = 0
    MID = 1
    UP = 2


# Min and Max PWMs for rotor speed
ZERO_ROTOR_SPEED = 1000
ABSOLUTE_MAX_PWM = 1900




class RadioDataParser:
    """RadioDataParser Class provides functions that help 
    in processing and encoding radio data.
    """
    def __init__(self):
        """Constructor
        """
        self.m_channelData = None
        self.rawRatePercentage = None
        self.switchValue = None

    def mapRadioToAngle(self, x):
        """Maps radio stick positions to corresponding angles in radians linearly.

        :param x: Stick position data.
        :type x: int
        :return: angle in radians.
        :rtype: float
        """
        return -PITCH_MAX_RAD + (x - RADIO_STICK_MIN) / (RADIO_STICK_MAX - RADIO_STICK_MIN) * 2 * PITCH_MAX_RAD

    def mapTrimmerToPercentage(self, x):
        """Linearly maps radio timmer or stick data to percentage [0, 1].

        :param x: Stick or trimmer position data.
        :type x: int
        :return: Percentage in range [0, 1].
        :rtype: float
        """
        percentage = (x - RADIO_STICK_MIN) / (RADIO_STICK_MAX - RADIO_STICK_MIN)
        return max(min(percentage, 1), 0)

    def pitchReferenceAngleRad(self):
        """Maps pitch stick data to reference pitch angle in radians.

        :return: reference pitch angle in radians.
        :rtype: float
        """
        return self.mapRadioToAngle(self.m_channelData[RADIO_CHANNEL_PITCH])

    def rollReferenceAngleRad(self):
        """Maps roll stick data to reference roll angle in radians.

        :return: reference roll angle in radians.
        :rtype: float
        """
        return self.mapRadioToAngle(self.m_channelData[RADIO_CHANNEL_ROLL])

    def yawRateReferenceRadSec(self):
        """Maps yaw stick data to reference yaw angle in radians.

        :return: reference yaw angle in radians.
        :rtype: float
        """
        self.rawRatePercentage = self.mapTrimmerToPercentage(self.m_channelData[RADIO_CHANNEL_YAW_RATE])
        return -RADIO_MAX_YAW_RATE_RAD_SEC + RADIO_MAX_YAW_RATE_RAD_SEC * self.rawRatePercentage
    
    def throttleReferencePercentage(self):
        """Maps throttle stick data to reference percentage.

        :return: percentage reference of throttle.
        :rtype: float
        """
        return self.mapTrimmerToPercentage(self.m_channelData[RADIO_CHANNEL_THROTTLE])

    def armed(self):
        """Checks if the arm switch (switch B) has been toggled.

        :return: Arm status. True if armed else False.
        :rtype: bool
        """
        return self.m_channelData[RADIO_CHANNEL_SWITCH_B] >= 1500

    def kill(self):
        """Checks if the kill switch (switch A) has been toggled.

        :return: Kill status. True if killed else False.
        :rtype: bool
        """
        return self.m_channelData[RADIO_CHANNEL_SWITCH_A] >= 1500

    def switchC(self):
        """Checks the position of the three-way switch C.

        :return: Three-way switch position. DOWN = 0, MID = 1, UP = 2.
        :rtype: Of class ThreeWaySwitch, extends Enum
        """
        self.switchValue = self.m_channelData[RADIO_CHANNEL_SWITCH_C]
        if self.switchValue <= 450:
            return ThreeWaySwitch.DOWN
        elif self.switchValue <= 1200:
            return ThreeWaySwitch.MID
        return ThreeWaySwitch.UP

    def switchD(self):
        """Checks the positon of the switch D.

        :return: Switch D position.
        :rtype: bool
        """
        return self.m_channelData[RADIO_CHANNEL_SWITCH_D] >= 1500

    def trimmerVRAPercentage(self):
        """Maps Variable Resistor A data to percentage.

        :return: VRA percentage in range [0, 1].
        :rtype: float
        """
        return self.mapTrimmerToPercentage(self.m_channelData[RADIO_CHANNEL_VRA])

    def trimmerVRCPercentage(self):
        """Maps Variable Resistor C data to percentage.

        :return: VRC percentage in range [0, 1].
        :rtype: float
        """
        return self.mapTrimmerToPercentage(self.m_channelData[RADIO_CHANNEL_VRC])

    def trimmerVRBPercentage(self):
        """Maps Variable Resistor B data to percentage.

        :return: VRB percentage in range [0, 1].
        :rtype: float
        """
        return self.mapTrimmerToPercentage(self.m_channelData[RADIO_CHANNEL_VRB])

    def trimmerVREPercentage(self):
        """Maps Variable Resistor E data to percentage.

        :return: VRE percentage in range [0, 1].
        :rtype: float
        """
        return self.mapTrimmerToPercentage(self.m_channelData[RADIO_CHANNEL_VRE])
    
    def mapPrcnt(self, percentage, minVal, maxVal):
        """Linearly maps percentage data to range [minVal, maxVal].

        :param percentage: Value of percentage, in range [0, 1], to be mapped.
        :type percentage: float
        :param minVal: Lower boundary of the mapped data.
        :type minVal: int/ float
        :param maxVal: Upper boundary of the mapped data.
        :type maxVal: int/ float
        :return: mapped data in range [minVal, maxVal].
        :rtype: int/ float
        """
        return minVal + percentage * (maxVal - minVal)
    
    def formatRadioDataForSending(self):
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
              (This is given the first position because it is the arm switch)
            - bit `|A|` indicates switch A's position 
              (This is the kill switch)
            - bits `|C|c|` together indicate switch C's position
            - bit `|D|` indicates switch D's position  

            For switches `A`, `B`, and `D` (since these are only two-way switches), each 
            were assigned a single bit with 0 indicating that the switch is in off state
            and 1 otherwise. For switch C, as it is a three-way switch, it was assigned with
            two bits with 00 = DOWN, 01 = MID, and 10 = UP.    
        
        :return: Formatted string that contains the processed radio data, 
                 where each data point is seperated by a comma.
        """
        reArrangedYPRTData = [self.yawRateReferenceRadSec(), self.pitchReferenceAngleRad(), self.rollReferenceAngleRad(), self.mapPrcnt(self.throttleReferencePercentage(), ZERO_ROTOR_SPEED, ABSOLUTE_MAX_PWM)]
        bitEncodedSwithcesData = (self.armed() << 4) | (self.kill() << 3) | (self.switchC() << 1) | self.switchD()
        reArrangedABCETrimmersData = [self.trimmerVRAPercentage(), self.trimmerVRBPercentage(), self.trimmerVRCPercentage(), self.trimmerVREPercentage()]

        reArrangedData = reArrangedYPRTData + reArrangedABCETrimmersData
        
        return ",".join(map(lambda x: str(x)[:5], reArrangedData)) + f",{bitEncodedSwithcesData}"



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

DOWN = "DOWN"
MID = "MID"
UP = "UP"



ZERO_ROTOR_SPEED = 1000
ABSOLUTE_MAX_PWM = 1900


class RadioDataParser:
    def __init__(self):
        self.m_channelData = None
        self.rawRatePercentage = None
        self.switchValue = None
        self.ThreeWaySwitch = {
            "DOWN" : 0,
            "MID" : 1,
            "UP" : 2
        }

    def mapRadioToAngle(self, x):
        return -PITCH_MAX_RAD + (float)(x - RADIO_STICK_MIN) / ((float)(RADIO_STICK_MAX - RADIO_STICK_MIN)) * 2 * PITCH_MAX_RAD

    def mapTrimmerToPercentage(self, x):
        percentage = (float)(x - RADIO_STICK_MIN) / ((float)(RADIO_STICK_MAX - RADIO_STICK_MIN))
        return percentage if percentage >= 0 else 0

    def pitchReferenceAngleRad(self):
        return self.mapRadioToAngle(self.m_channelData[RADIO_CHANNEL_PITCH])

    def rollReferenceAngleRad(self):
        return self.mapRadioToAngle(self.m_channelData[RADIO_CHANNEL_ROLL])

    def yawRateReferenceRadSec(self):
        self.rawRatePercentage = self.mapTrimmerToPercentage(self.m_channelData[RADIO_CHANNEL_YAW_RATE]);
        return -RADIO_MAX_YAW_RATE_RAD_SEC + RADIO_MAX_YAW_RATE_RAD_SEC * self.rawRatePercentage
    
    def throttleReferencePercentage(self):
        return self.mapTrimmerToPercentage(self.m_channelData[RADIO_CHANNEL_THROTTLE])

    def armed(self):
        return self.m_channelData[RADIO_CHANNEL_SWITCH_B] >= 1500

    def kill(self):
        return self.m_channelData[RADIO_CHANNEL_SWITCH_A] >= 1500

    def switchC(self):
        self.switchValue = self.m_channelData[RADIO_CHANNEL_SWITCH_C];
        if self.switchValue <= 450:
            return self.ThreeWaySwitch[DOWN]
        elif self.switchValue <= 1200:
            return self.ThreeWaySwitch[MID]
        return self.ThreeWaySwitch[UP]

    def switchD(self):
        return self.m_channelData[RADIO_CHANNEL_SWITCH_D] >= 1500

    def trimmerVRAPercentage(self):
        return self.mapTrimmerToPercentage(self.m_channelData[RADIO_CHANNEL_VRA])

    def trimmerVRCPercentage(self):
        return self.mapTrimmerToPercentage(self.m_channelData[RADIO_CHANNEL_VRC])

    def trimmerVRBPercentage(self):
        return self.mapTrimmerToPercentage(self.m_channelData[RADIO_CHANNEL_VRB])

    def trimmerVREPercentage(self):
        return self.mapTrimmerToPercentage(self.m_channelData[RADIO_CHANNEL_VRE])
    
    def mapPrcnt(self, percentage, minVal, maxVal):
        return minVal + percentage * (maxVal - minVal)
    
    def encapsulateRadioData(self):
        reArrangedYPRTData = [self.yawRateReferenceRadSec(), self.pitchReferenceAngleRad(), self.rollReferenceAngleRad(), self.mapPrcnt(self.throttleReferencePercentage(), ZERO_ROTOR_SPEED, ABSOLUTE_MAX_PWM)]
        bitEncodedSwithcesData = (self.armed() << 4) | (self.kill() << 3) | (self.switchC() << 1) | self.switchD()
        reArrangedABCETrimmersData = [self.trimmerVRAPercentage(), self.trimmerVRBPercentage(), self.trimmerVRCPercentage(), self.trimmerVREPercentage()]

        reArrangedData = reArrangedYPRTData + reArrangedABCETrimmersData
        
        return ",".join(map(lambda x: str(x)[:5], reArrangedData)) + f",{bitEncodedSwithcesData}"

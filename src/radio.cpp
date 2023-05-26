#include "radio.hpp"

#define RADIO_CHANNEL_YAW_RATE 0
#define RADIO_CHANNEL_PITCH 1
#define RADIO_CHANNEL_THROTTLE 2
#define RADIO_CHANNEL_ROLL 3
#define RADIO_CHANNEL_VRA 5
#define RADIO_CHANNEL_VRB 7
#define RADIO_CHANNEL_VRC 6
#define RADIO_CHANNEL_VRE 11
#define RADIO_CHANNEL_SWITCH_A 9
#define RADIO_CHANNEL_SWITCH_B 8
#define RADIO_CHANNEL_SWITCH_C 4
#define RADIO_CHANNEL_SWITCH_D 10

namespace bzzz
{
    Radio::Radio(){};

    float mapRadioToAngle(int x)
    {
        return -PITCH_MAX_RAD + (float)(x - RADIO_STICK_MIN) / ((float)(RADIO_STICK_MAX - RADIO_STICK_MIN)) * 2 * PITCH_MAX_RAD;
    }

    float mapTrimmerToPercentage(int x)
    {
        return (float)(x - RADIO_STICK_MIN) / ((float)(RADIO_STICK_MAX - RADIO_STICK_MIN));
    }

    bool Radio::readPiData(void)
    {
        String allDataFromPi;
        int data_count = 0;

        if (Serial.available() > 0)
        {
            allDataFromPi = Serial.readStringUntil('\n');
            data_count = 0;

            for (int i = 0; i < 16; i++, data_count++)
            {
                // take the substring from the start to the first occurence of a comma,
                // convert it to int and save it in the array
                // read the data into as dummy data and later check if the data is proper or not
                m_dummyChannelData[i] = allDataFromPi.substring(1, allDataFromPi.indexOf(",")).toInt();
                if(m_dummyChannelData[i] < 100 || m_dummyChannelData[i] > 1900) return false; //m_dummyChannelData[i] = 100;  // TODO: change 100 and 1900 to an appropriate value later
                // else if (m_dummyChannelData[i] > 1900) m_dummyChannelData[i] = 1900;
                

                // cut the channelData string after the first occurence of a comma
                allDataFromPi = allDataFromPi.substring(allDataFromPi.indexOf(",") + 1);
            }
            if(data_count == 15) for(int i = 0; i < 16; i++) m_channelData[i] = m_dummyChannelData[i];
            else return false;
            if(m_channelData[RADIO_CHANNEL_THROTTLE] < 0) m_channelData[RADIO_CHANNEL_THROTTLE] = 0;
            return true;
        }
        return false;
    }

    float Radio::pitchReferenceAngleRad()
    {
        return mapRadioToAngle(m_channelData[RADIO_CHANNEL_PITCH]);
    }

    float Radio::rollReferenceAngleRad()
    {
        return mapRadioToAngle(m_channelData[RADIO_CHANNEL_ROLL]);
    }

    float Radio::yawRateReferenceRadSec()
    {
        float rawRatePercentage = mapTrimmerToPercentage(m_channelData[RADIO_CHANNEL_YAW_RATE]);
        return -RADIO_MAX_YAW_RATE_RAD_SEC + RADIO_MAX_YAW_RATE_RAD_SEC * rawRatePercentage;
    }

    float Radio::throttleReferencePercentage()
    {
        return mapTrimmerToPercentage(m_channelData[RADIO_CHANNEL_THROTTLE]);
    }

    bool Radio::armed()
    {
        return m_channelData[RADIO_CHANNEL_SWITCH_B] >= 1500;
    }

    bool Radio::kill()
    {
        return m_channelData[RADIO_CHANNEL_SWITCH_A] >= 1500;
    }

    ThreeWaySwitch Radio::switchC()
    {
        int switchValue = m_channelData[RADIO_CHANNEL_SWITCH_C];
        if (switchValue <= 450)
        {
            return ThreeWaySwitch::DOWN;
        }
        else if (switchValue <= 1200)
        {
            return ThreeWaySwitch::MID;
        }
        return ThreeWaySwitch::UP;
    }

    bool Radio::switchD()
    {
        return m_channelData[RADIO_CHANNEL_SWITCH_D] >= 1500;
    }

    float Radio::trimmerVRAPercentage()
    {
        return mapTrimmerToPercentage(m_channelData[RADIO_CHANNEL_VRA]);
    }

    float Radio::trimmerVRCPercentage()
    {
        return mapTrimmerToPercentage(m_channelData[RADIO_CHANNEL_VRC]);
    }

    float Radio::trimmerVRBPercentage()
    {
        return mapTrimmerToPercentage(m_channelData[RADIO_CHANNEL_VRB]);
    }

    float Radio::trimmerVREPercentage()
    {
        return mapTrimmerToPercentage(m_channelData[RADIO_CHANNEL_VRE]);
    }

    void Radio::waitForArmCommand()
    {
        readPiData();
        delay(1000); // TODO is this delay necessary?
        while (!armed())
        {
            readPiData();
        }
    }

}

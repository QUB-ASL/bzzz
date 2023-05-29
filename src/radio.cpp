#include "radio.hpp"

#define RADIO_CHANNEL_YAW_RATE 0
#define RADIO_CHANNEL_PITCH 1
#define RADIO_CHANNEL_ROLL 2
#define RADIO_CHANNEL_THROTTLE 3
#define RADIO_CHANNEL_VRA 4
#define RADIO_CHANNEL_VRB 5
#define RADIO_CHANNEL_VRC 6
#define RADIO_CHANNEL_VRE 7
#define RADIO_SWITCH_A_BIT 0b01000
#define RADIO_SWITCH_B_BIT 0b10000
#define RADIO_SWITCH_C_BITS 0b00110
#define RADIO_SWITCH_D_BIT 0b00001

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
            
            if(allDataFromPi.substring(0, allDataFromPi.indexOf(",")) != "S") return false;
            // cut the channelData string after the first occurence of a comma
            allDataFromPi = allDataFromPi.substring(allDataFromPi.indexOf(",") + 1);

            for (int i = 0; i < 8; i++, data_count++)
            {
                // take the substring from the start to the first occurence of a comma,
                // convert it to int and save it in the array
                // save the data to a dummy array
                m_dummyRefData[i] = allDataFromPi.substring(0, allDataFromPi.indexOf(",")).toFloat();

                // cut the channelData string after the first occurence of a comma
                allDataFromPi = allDataFromPi.substring(allDataFromPi.indexOf(",") + 1);
            }
            // Check if 8 data points are received and return false if not. 
            // if yes, copy the data to the actual array
            // this helps to retain previous data if corrupted data is received
            if(data_count != 8) 
            {
                return false;
            }
            else 
            { 
                for(int i = 0; i < 8; i++) 
                {
                    m_refData[i] = m_dummyRefData[i];
                }
            }

            // get the encoded switches data
            m_dummyEncodedSwtchsData = allDataFromPi.substring(0, allDataFromPi.indexOf(",")).toInt();
            // the max value possible for encoded switch data in binary is 0b{1 1 10 1} = 29
            if (m_dummyEncodedSwtchsData <0 || m_dummyEncodedSwtchsData > 29)
            {
                return false;
            }
            else
            {
                m_encodedSwitchesData = m_dummyEncodedSwtchsData;
            }
            return true;
        }
        return false;
    }

    float Radio::pitchReferenceAngleRad()
    {
        return m_refData[RADIO_CHANNEL_PITCH];
    }

    float Radio::rollReferenceAngleRad()
    {
        return m_refData[RADIO_CHANNEL_ROLL];
    }

    float Radio::yawRateReferenceRadSec()
    {
        return m_refData[RADIO_CHANNEL_YAW_RATE];
    }

    float Radio::throttleReferencePWM()
    {
        return m_refData[RADIO_CHANNEL_THROTTLE];
    }

    float Radio::throttleReferencePercentage()
    {
        return m_refData[RADIO_CHANNEL_THROTTLE]/1000 - 1;
    }

    bool Radio::armed()
    {
        return m_encodedSwitchesData & RADIO_SWITCH_B_BIT;
    }

    bool Radio::kill()
    {
        return m_encodedSwitchesData & RADIO_SWITCH_A_BIT;
    }

    ThreeWaySwitch Radio::switchC()
    {
        switch((m_encodedSwitchesData & RADIO_SWITCH_C_BITS) >> 1)
        {
            case 0:
                return ThreeWaySwitch::DOWN;
            case 1:
                return ThreeWaySwitch::MID;
            case 2:
                return ThreeWaySwitch::UP;
            default:
                return ThreeWaySwitch::DOWN;
        }
    }

    bool Radio::switchD()
    {
        return m_encodedSwitchesData & RADIO_SWITCH_D_BIT;
    }

    float Radio::trimmerVRAPercentage()
    {
        return m_refData[RADIO_CHANNEL_VRA];
    }

    float Radio::trimmerVRCPercentage()
    {
        return m_refData[RADIO_CHANNEL_VRC];
    }

    float Radio::trimmerVRBPercentage()
    {
        return m_refData[RADIO_CHANNEL_VRB];
    }

    float Radio::trimmerVREPercentage()
    {
        return m_refData[RADIO_CHANNEL_VRE];
    }

    void Radio::waitForArmCommand()
    {
        readPiData();
        delay(20); // TODO is this delay necessary?
        while (!armed())
        {
            readPiData();
            // Serial.println(m_encodedSwitchesData);
        }
    }

}

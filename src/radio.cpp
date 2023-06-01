#include "radio.hpp"

#define RADIO_CHANNEL_YAW_RATE 0
#define RADIO_CHANNEL_PITCH 1
#define RADIO_CHANNEL_ROLL 2
#define RADIO_CHANNEL_THROTTLE 3
#define RADIO_CHANNEL_VRA 4
#define RADIO_CHANNEL_VRB 5
#define RADIO_CHANNEL_VRC 6
#define RADIO_CHANNEL_VRE 7
/**
 * In the processed radio data sent from R-Pi, the last element sent is an
 * integer in which the switches' position data is encoded as follows
 *      For switches A, B, and D (since these are only two-way switches), each 
 *      were assigned a single bit with 0 indicating that the switch is in off state
 *      and 1 otherwise. For switch C, as it is a three-way switch, it was assigned with
 *      two bits with 00 = DOWN, 01 = MID, and 10 = UP.
 * This encoded data is formated as follows
 *
 *      |0|0|0|B|A|C|c|D| this is the Least-significant byte of the received integer.
 *      In which bit |B| indicates switch B's position (This is given the first position because it is the arm switch)
 *               bit |A| indicates switch A's position (This is the kill switch)
 *               bits |C|c| together indicate switch C's position
 *               bit |D| indicates switch D's position      
*/
#define RADIO_SWITCH_A_BIT 0b01000  // Bit position of switch A
#define RADIO_SWITCH_B_BIT 0b10000  // Bit position of switch B
#define RADIO_SWITCH_C_BITS 0b00110  // Bits' position of switch C
#define RADIO_SWITCH_D_BIT 0b00001  // Bit position of switch D


// These are the number of data channles. We do not count the switch data channels.
#define NUM_RADIO_CHANNELS 8

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

            for (int i = 0; i < NUM_RADIO_CHANNELS || allDataFromPi != ""; i++, data_count++)
            {
                // take the substring from the start to the first occurence of a comma,
                // convert it to int and save it in the array
                // save the data to a dummy array
                m_rawRefData[i] = allDataFromPi.substring(0, allDataFromPi.indexOf(",")).toFloat();

                // cut the channelData string after the first occurence of a comma
                allDataFromPi = allDataFromPi.substring(allDataFromPi.indexOf(",") + 1);
            }
            // Check if 8 data points are received and return false if not. 
            // if yes, copy the data to the actual array
            // this helps to retain previous data if corrupted data is received
            if(data_count != NUM_RADIO_CHANNELS) 
            {
                return false;
            }
            for(int i = 0; i < NUM_RADIO_CHANNELS; i++) 
            {
                m_refData[i] = m_rawRefData[i];
            }

            // get the encoded switches data
            m_rawEncodedSwtchsData = allDataFromPi.substring(0, allDataFromPi.indexOf(",")).toInt();
            // the max value possible for encoded switch data in binary is 0b{1 1 10 1} = 29
            if (m_rawEncodedSwtchsData <0 || m_rawEncodedSwtchsData > 29)
            {
                return false;
            }
            m_encodedSwitchesData = m_rawEncodedSwtchsData;
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
        // Since PWM range is [1000, 2000], we subtract 1000 to calculate the percentage
        //   percentage = (Referance_PWM - 1000)/1000
        //=> percentage = Reference_PWM/1000 - 1
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
        delay(20);
        while (!armed())
        {
            readPiData();
        }
    }

}

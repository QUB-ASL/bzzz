#include "raspberryEsp32Interface.hpp"

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
#define RADIO_SWITCH_C_BITS 0b00110 // Bits' position of switch C
#define RADIO_SWITCH_D_BIT 0b00001  // Bit position of switch D

// These are the number of data channles. We do not count the switch data channels.
#define NUM_RADIO_CHANNELS 8

namespace bzzz
{
    RaspberryEsp32Interface::RaspberryEsp32Interface(bool replyWithFlightData /*=false*/)
    {
        this->m_replyWithFlightData = replyWithFlightData;
    };

    bool RaspberryEsp32Interface::readPiData()
    {
        String allDataFromPi;
        int data_count = 0;

        if (Serial.available() > 0)
        {
            allDataFromPi = Serial.readStringUntil('\n');

            if (allDataFromPi.substring(0, allDataFromPi.indexOf(",")) != "S")
                return false;
            // cut the channelData string after the first occurence of a comma
            allDataFromPi = allDataFromPi.substring(allDataFromPi.indexOf(",") + 1);

            for (int i = 0; i < NUM_RADIO_CHANNELS && allDataFromPi != ""; i++, data_count++)
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
            if (data_count != NUM_RADIO_CHANNELS)
            {
                return false;
            }
            for (int i = 0; i < NUM_RADIO_CHANNELS; i++)
            {
                m_refData[i] = m_rawRefData[i];
            }

            // get the encoded switches data
            m_rawEncodedSwtchsData = allDataFromPi.substring(0, allDataFromPi.indexOf(",")).toInt();
            // the max value possible for encoded switch data in binary is 0b{1 1 10 1} = 29
            if (m_rawEncodedSwtchsData < 0 || m_rawEncodedSwtchsData > 29)
            {
                return false;
            }
            m_encodedSwitchesData = m_rawEncodedSwtchsData;
            return true;
        }
        return false;
    }

    void RaspberryEsp32Interface::sendFlightDataToPi(
        float q1,
        float q2,
        float q3,
        float ax,
        float ay,
        float az,
        float motorFL,
        float motorFR,
        float motorBL,
        float motorBR)
    {
        if (this->m_replyWithFlightData)
        {
            // if replyWithFlightData is enabled, send flight data to Pi
            Serial.print("FD: ");
            Serial.print(q1);
            Serial.print(' ');
            Serial.print(q2);
            Serial.print(' ');
            Serial.print(q3);
            Serial.print(' ');
            Serial.print(ax);
            Serial.print(' ');
            Serial.print(ay);
            Serial.print(' ');
            Serial.print(az);
            Serial.print(' ');
            Serial.print(motorFL);
            Serial.print(' ');
            Serial.print(motorFR);
            Serial.print(' ');
            Serial.print(motorBL);
            Serial.print(' ');
            Serial.println(motorBR);
        }
    }

    float RaspberryEsp32Interface::pitchReferenceAngleRad()
    {
        return m_refData[RADIO_CHANNEL_PITCH];
    }

    float RaspberryEsp32Interface::rollReferenceAngleRad()
    {
        return m_refData[RADIO_CHANNEL_ROLL];
    }

    float RaspberryEsp32Interface::yawRateReferenceRadSec()
    {
        return m_refData[RADIO_CHANNEL_YAW_RATE];
    }

    float RaspberryEsp32Interface::throttleReferencePWM()
    {
        return m_refData[RADIO_CHANNEL_THROTTLE];
    }

    float RaspberryEsp32Interface::throttleReferencePercentage()
    {
        // Since PWM range is [1000, 2000], we subtract 1000 to calculate the percentage
        //   percentage = (Referance_PWM - 1000)/1000
        //=> percentage = Reference_PWM/1000 - 1
        return m_refData[RADIO_CHANNEL_THROTTLE] / 1000 - 1;
    }

    bool RaspberryEsp32Interface::armed()
    {
        return m_encodedSwitchesData == RADIO_SWITCH_B_BIT && throttleReferencePercentage() < 0.05 ;
    }

    bool RaspberryEsp32Interface::kill()
    {
        return m_encodedSwitchesData & RADIO_SWITCH_D_BIT;
    }

    ThreeWaySwitch RaspberryEsp32Interface::switchC()
    {
        switch ((m_encodedSwitchesData & RADIO_SWITCH_C_BITS) >> 1)
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

    bool RaspberryEsp32Interface::switchD()
    {
        return m_encodedSwitchesData & RADIO_SWITCH_D_BIT;
    }

    float RaspberryEsp32Interface::trimmerVRAPercentage()
    {
        return m_refData[RADIO_CHANNEL_VRA];
    }

    float RaspberryEsp32Interface::trimmerVRCPercentage()
    {
        return m_refData[RADIO_CHANNEL_VRC];
    }

    float RaspberryEsp32Interface::trimmerVRBPercentage()
    {
        return m_refData[RADIO_CHANNEL_VRB];
    }

    float RaspberryEsp32Interface::trimmerVREPercentage()
    {
        return m_refData[RADIO_CHANNEL_VRE];
    }

    void RaspberryEsp32Interface::waitForArmCommand()
    {
        float temp[6];
        readPiData();
        sendFlightDataToPi(-1, -1, -1, -1, -1, -1, -1, -1, -1, -1);
        delay(20);
        while (!armed())
        {
            readPiData();
            sendFlightDataToPi(-1, -1, -1, -1, -1, -1, -1, -1, -1, -1);
        }
    }

}

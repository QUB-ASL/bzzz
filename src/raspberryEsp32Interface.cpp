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
 * For switches A, B, and D (since these are only two-way switches), each
 * were assigned a single bit with 0 indicating that the switch is in off state
 * and 1 otherwise. For switch C, as it is a three-way switch, it was assigned with
 * two bits with 00 = DOWN, 01 = MID, and 10 = UP.
 * This encoded data is formated as follows
 *
 * |0|0|0|B|A|C|c|D| this is the Least-significant byte of the received integer.
 * In which bit |B| indicates switch B's position (This is given the first position because it is the arm switch)
 * bit |A| indicates switch A's position (This is the kill switch)
 * bits |C|c| together indicate switch C's position
 * bit |D| indicates switch D's position
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
        bool gotGoodPacket = false;

        // Drain ALL complete lines currently buffered, keep only the newest
        // valid one. Prevents backlog build-up and mid-line corruption when
        // the loop falls behind the Pi's send rate.
        while (Serial.available() > 0)
        {
            String allDataFromPi = Serial.readStringUntil('\n');

            if (allDataFromPi.substring(0, allDataFromPi.indexOf(",")) != "S")
                continue;

            allDataFromPi = allDataFromPi.substring(allDataFromPi.indexOf(",") + 1);

            float candidate[NUM_RADIO_CHANNELS];
            int data_count = 0;

            for (int i = 0; i < NUM_RADIO_CHANNELS && allDataFromPi != ""; i++, data_count++)
            {
                candidate[i] = allDataFromPi.substring(0, allDataFromPi.indexOf(",")).toFloat();
                allDataFromPi = allDataFromPi.substring(allDataFromPi.indexOf(",") + 1);
            }

            if (data_count != NUM_RADIO_CHANNELS)
                continue;

            // Per-channel sanity bounds — reject the whole packet if any
            // channel is outside its physically possible range. Ranges
            // padded slightly beyond the Pi's own mapped output.
            bool sane = true;
            sane &= (candidate[RADIO_CHANNEL_YAW_RATE] > -60.0f  && candidate[RADIO_CHANNEL_YAW_RATE] < 60.0f);
            sane &= (candidate[RADIO_CHANNEL_PITCH]    > -0.60f  && candidate[RADIO_CHANNEL_PITCH]    < 0.60f);
            sane &= (candidate[RADIO_CHANNEL_ROLL]     > -0.60f  && candidate[RADIO_CHANNEL_ROLL]     < 0.60f);
            sane &= (candidate[RADIO_CHANNEL_THROTTLE] > 850.0f  && candidate[RADIO_CHANNEL_THROTTLE] < 2050.0f);
            sane &= (candidate[RADIO_CHANNEL_VRA] > -0.1f && candidate[RADIO_CHANNEL_VRA] < 1.1f);
            sane &= (candidate[RADIO_CHANNEL_VRB] > -0.1f && candidate[RADIO_CHANNEL_VRB] < 1.1f);
            sane &= (candidate[RADIO_CHANNEL_VRC] > -0.1f && candidate[RADIO_CHANNEL_VRC] < 1.1f);
            sane &= (candidate[RADIO_CHANNEL_VRE] > -0.1f && candidate[RADIO_CHANNEL_VRE] < 1.1f);

            if (!sane)
                continue;

            int encoded = allDataFromPi.substring(0, allDataFromPi.indexOf(",")).toInt();
            if (encoded < 0 || encoded > 29)
                continue;

            // this line passed every check — accept it, keep scanning for
            // any newer line still sitting in the buffer
            for (int i = 0; i < NUM_RADIO_CHANNELS; i++)
                m_refData[i] = candidate[i];
            m_encodedSwitchesData = encoded;
            gotGoodPacket = true;
        }

        return gotGoodPacket;
    }

    #if UAV_TYPE == UAV_TYPE_QUADCOPTER
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
            Serial.print(q1, 4); Serial.print(' ');
            Serial.print(q2, 4); Serial.print(' ');
            Serial.print(q3, 4); Serial.print(' ');
            Serial.print(wx, 3); Serial.print(' ');
            Serial.print(wy, 3); Serial.print(' ');
            Serial.print(wz, 3); Serial.print(' ');
            Serial.print(motorFL, 0); Serial.print(' ');
            Serial.print(motorFR, 0); Serial.print(' ');
            Serial.print(motorBL, 0); Serial.print(' ');
            Serial.println(motorBR, 0);
        }
    }
    #elif UAV_TYPE == UAV_TYPE_HEXACOPTER
    void RaspberryEsp32Interface::sendFlightDataToPi(
        float q0,
        float q1,
        float q2,
        float q3,
        float ax,
        float ay,
        float az,
        float motorFL,
        float motorFR,
        float motorBL,
        float motorBR,
        float motorML,
        float motorMR,
        float q0p,
        float q1p,
        float q2p,
        float q3p,
        float wxp,
        float wyp,
        float wzp,
        const float *J,
        int nJ)   
        
    

    {
        if (this->m_replyWithFlightData)
        {
            char buf[320];
            int n = snprintf(buf, sizeof(buf),
                "FD: %.4f %.4f %.4f %.4f %.3f %.3f %.3f "
                "%.0f %.0f %.0f %.0f %.0f %.0f",
                q0, q1, q2, q3, ax, ay, az,
                motorFL, motorFR, motorBL, motorBR, motorML, motorMR);

                for (int i = 0; i < nJ && n < (int)sizeof(buf) - 12; i++)
                     n += snprintf(buf + n, sizeof(buf) - n, " %.3f", J[i]);

            Serial.println(buf);
        }
    }
    #endif

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
        //   percentage = (Reference_PWM - 1000)/1000
        //=> percentage = Reference_PWM/1000 - 1
        return m_refData[RADIO_CHANNEL_THROTTLE] / 1000 - 1;
    }

    bool RaspberryEsp32Interface::switchA()
    {
        return m_encodedSwitchesData & RADIO_SWITCH_A_BIT;
    }
    
    bool RaspberryEsp32Interface::canArm()
    {
        // We only want to arm the motor when the arm switch is down and the rest are up 
        // therefore we want the m_encodedSwitchesData == RADIO_SWITCH_B_BIT.
        // We also only want to arm when the throttle is down
        // therefore throttleReferencePercentage() < MAX_ARMING_THROTTLE_PERCENTAGE (default 5%)
        bool isOnlyArmSwitchOn = m_encodedSwitchesData == RADIO_SWITCH_B_BIT;
        bool isThrottleDown = throttleReferencePercentage() < MAX_ARMING_THROTTLE_PERCENTAGE;

        return isOnlyArmSwitchOn && isThrottleDown;
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
        Serial.println(" ENTERED waitForArmCommand()");

        float temp[6];
        readPiData();
        
        // Send initial dummy packets based on layout type
        #if UAV_TYPE == UAV_TYPE_QUADCOPTER
        sendFlightDataToPi(-1, -1, -1, -1, -1, -1, -1, -1, -1, -1);
        #elif UAV_TYPE == UAV_TYPE_HEXACOPTER
       static const float jDummy[7] = {-1,-1,-1,-1,-1,-1,-1};
        sendFlightDataToPi(-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
                           -1,-1,-1,-1,-1,-1,-1, jDummy, 7);
        #endif

        delay(20);
        while (!canArm())
        {
            Serial.print("Encoded = ");
            Serial.print(m_encodedSwitchesData);

            Serial.print(" | Throttle = ");
            Serial.print(throttleReferencePercentage());

            Serial.print(" | A =");
            Serial.print(switchA());

            Serial.print(" | B =");
            Serial.print((m_encodedSwitchesData & RADIO_SWITCH_B_BIT)!= 0);

            Serial.print(" C =");
            Serial.print((int)switchC());

            Serial.print(" D =");
            Serial.print(switchD());

            Serial.print( " | canArm =");
            Serial.print(canArm());

            readPiData();

            
            // Send waiting packets based on layout type
            #if UAV_TYPE == UAV_TYPE_QUADCOPTER
            sendFlightDataToPi(-1, -1, -1, -1, -1, -1, -1, -1, -1, -1);
            #elif UAV_TYPE == UAV_TYPE_HEXACOPTER
           static const float jDummy[7] = {-1,-1,-1,-1,-1,-1,-1};
           sendFlightDataToPi(-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
                           -1,-1,-1,-1,-1,-1,-1, jDummy, 7);
            #endif
        }
    }

}
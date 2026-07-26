#include "config.hpp"

#ifndef RADIO_H
#define RADIO_H

namespace bzzz
{

    /**
     * Possible values of 3-way switch
     */
    enum ThreeWaySwitch
    {
        DOWN = 0,
        MID = 1,
        UP = 2
    };

    class RaspberryEsp32Interface
    {

    private:
        /**
         * Array of reference data from radio with information as follows
         * index    Variable
         * 0          yaw rate in rad/s
         * 1          pitch in rad
         * 2          roll in rad
         * 3          throttle in PWM range [1000, 2000]
         * 4          % trim A
         * 5          % trim B
         * 6          % trim C
         * 7          % trim E
         *
         * A substitute variable to load the read data from Raspberry Pi.
         * This data is tested for corruption before copying to the actual variable.
         */
        float m_rawRefData[8];

        /**
         * The actual variable to store un-corrupt data.
         * This data will be used as reference for the flight controller.
         */
        float m_refData[8];

        /**
         * The last part of the radio data from R-Pi is a 5-bit data encoding
         * the positions of switches as follows
         * bit index    Variable
         * 4(MSB)     Switch B (Arm switch  ){1 if switch_is_on else 0}
         * 3          Switch A (Kill switch ){1 if switch_is_on else 0}
         * 2, 1       Switch C (3-way switch){00 for position DOWN, 01
         * for position MID, 10 for position UP}
         * 0(LSB)     Switch D (2-way switch){1 if switch_is_on else 0}
         *
         * A substitute variable to load the encoded switch read data from Raspberry Pi.
         * This data is tested for corruption before copying to the actual variable.
         */
        int m_rawEncodedSwtchsData;

        /**
         * The actual variable to store un-corrupt data.
         * This is the data that will be used to take the some associated logial decisions.
         */
        int m_encodedSwitchesData;

        /**
         * Boolean to enable sending IMU data to Pi whenever ESP receives radio data
         * if True: replies with IMU data;
         */
        bool m_replyWithFlightData;

    public:
        /**
         * @brief RaspberryEsp32Interface class constructor
         * @param replyWithFlightData enables replying to Pi with flight data whenever radio data from Pi is received.
         */
        RaspberryEsp32Interface(bool replyWithFlightData = false);

        /**
         * @brief Read the receiver data sent from Pi and send
         * @return true iff new data was received from RPi
         */
        bool readPiData();

        /**
         * @brief pitch reference from RC in rad
         */
        float pitchReferenceAngleRad();

        /**
         * @brief roll reference from RC in rad
         */
        float rollReferenceAngleRad();

        /**
         * @brief throttle reference as a PWM (1000-2000), but capped at 1900
         */
        float throttleReferencePWM();

        /**
         * @brief throttle reference as a percentage (0-1)
         */
        float throttleReferencePercentage();

        /**
         * @brief yaw rate in rad/s
         *
         * The max yaw rate (abs) is 45deg/s
         */
        float yawRateReferenceRadSec();

        /**
         * @brief value of switch A
         */
        bool switchA();

        /**
         * @brief whether the motors can be armed
         *
         * For the motors to arm, the arm switch needs to be at the ON position
         * and the throttle stick must be down.
         */
        bool canArm();

        /**
         * @brief whether the kill switch is on
         */
        bool kill();

        /**
         * @brief value of switch C (low/mid/high)
         */
        ThreeWaySwitch switchC();

        /**
         * @brief value of switch D
         */
        bool switchD();

        /**
         * @brief value of trimmer VRA (0-1)
         */
        float trimmerVRAPercentage();

        /**
         * @brief value of trimmer VRB (0-1)
         */
        float trimmerVRBPercentage();
        /**
         * @brief value of trimmer VRC (0-1)
         */
        float trimmerVRCPercentage();

        /**
         * @brief value of trimmer VRE (0-1)
         */
        float trimmerVREPercentage();

        /**
         * Wait until the arm switch is at the ON position
         */
        void waitForArmCommand();

        /**
         * @brief send flight data: IMU data quaternions, accelerometer values, and motor PWM values
         * Conditional setup for Quadcopter layout (4 motors) vs Hexacopter layout (6 motors)
         */
        #if UAV_TYPE == UAV_TYPE_QUADCOPTER
        /**
         * @brief send flight data for Quadcopter layout
         * @param q1 1st element of current attitude quaternion
         * @param q2 2nd element of current attitude quaternion
         * @param q3 3rd element of current attitude quaternion
         * @param ax current acceleration along x-axis
         * @param ay current acceleration along y-axis
         * @param az current acceleration along z-axis
         * @param motorFL current Front-Left motor PWM control action
         * @param motorFR current Front-Right motor PWM control action
         * @param motorBL current Back-Left motor PWM control action
         * @param motorBR current Back-Right motor PWM control action
         */
        void sendFlightDataToPi( float q0,float q1, float q2, float q3, float ax, float ay, float az, 
                                float motorFL, float motorFR, float motorBL, float motorBR);

        #elif UAV_TYPE == UAV_TYPE_HEXACOPTER
        /**
         * @brief send flight data for Hexacopter layout
         * @param q1 1st element of current attitude quaternion
         * @param q2 2nd element of current attitude quaternion
         * @param q3 3rd element of current attitude quaternion
         * @param ax current acceleration along x-axis
         * @param ay current acceleration along y-axis
         * @param az current acceleration along z-axis
         * @param motorFL current Front-Left motor PWM control action
         * @param motorFR current Front-Right motor PWM control action
         * @param motorBL current Back-Left motor PWM control action
         * @param motorBR current Back-Right motor PWM control action
         * @param motorML current Middle-Left motor PWM control action
         * @param motorMR current Middle-Right motor PWM control action
         */
        void sendFlightDataToPi(float q0, float q1, float q2, float q3,
                float ax, float ay, float az,
                float motorFL, float motorFR, float motorBL, float motorBR,
                float motorML, float motorMR,
                float q0p, float q1p, float q2p, float q3p,
                float wxp, float wyp, float wzp,
                const float *J, int nJ);
        #endif

    }; /* end of class RaspberryEsp32Interface */

}

#endif /* RADIO_H */
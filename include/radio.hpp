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

    class Radio
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
         *            for position MID, 10 for position UP}
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

    public:
        Radio();

        /**
         * @brief Read the receiver data sent from Pi
         *
         * @return true iff new data was received from RPi
         */
        bool readPiData(void);

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
         * @brief whether the arm switch is on
         */
        bool armed();

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

    }; /* end of class Radio */

}

#endif /* RADIO_H */
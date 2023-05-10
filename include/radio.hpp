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
         * Channel    Variable
         * 1          yaw rate
         * 2          pitch
         * 3          throttle
         * 4          roll
         * 5          Switch C
         * 6          Trimmer VRA
         * 7          Trimmer VRC
         * 8          Trimmer VRB
         * 9          Switch B (for arming)
         * 10         Switch A (kill)
         * 11         Switch D
         * 12         Trimmer VRE
         */
        int channelData[16];

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
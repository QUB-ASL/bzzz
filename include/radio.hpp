#include "config.hpp"

#ifndef RADIO_H
#define RADIO_H

namespace bzzz
{   

    /**
     * Possible values of 3-way switch
    */
    enum ThreeWaySwitch {
        DOWN = 0,
        MID = 1,
        UP = 2
    };

    /**
     * @brief Read the receiver data sent from Pi
     */
    void readPiData(void);

    /**
     * @brief reformat receiver values
     */
    void readRadioData(
        int &radioThrottle, 
        int &radioRoll, 
        int &radioPitch, 
        int &radioYawRate, 
        int &radioSwitchC,
        int &radioVRA, 
        int &radioVRC, 
        int &radioVRB, 
        int &radioArm, 
        int &radioKill, 
        int &radioSwitchD, 
        int &radioVRE);
    
    /**
     * @brief pitch reference from RC in rad
     */
    float pitchReferenceAngleRad();
    /**
     * @brief roll reference from RC in rad
     */
    float rollReferenceAngleRad();
    /**
     * @brief throll reference as a percentage
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
     * @brief value of trimmer VRA
     */
    float trimmerVRAPercentage();
    /**
     * @brief value of trimmer VRB
     */
    float trimmerVRBPercentage();
    /**
     * @brief value of trimmer VRC
     */
    float trimmerVRCPercentage();
    /**
     * @brief value of trimmer VRE
     */
    float trimmerVREPercentage();


}

#endif
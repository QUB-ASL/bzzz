#include "config.hpp"

#ifndef RADIO_H
#define RADIO_H

namespace bzzz
{   
    /**
     * @brief Read the receiver data sent from Pi
     */
    void readPiData(void);

    /**
     * @brief reformat receiver values
     */
    void readRadioData(int &radioThrottle, int &radioRoll, int &radioPitch, int &radioYaw, int &radioSwitchC,
    int &radioVRA, int &radioVRC, int &radioVRB, int &radioArm, int &radioKill, int &radioSwitchD, int &radioVRE);

}

#endif
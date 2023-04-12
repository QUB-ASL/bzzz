#include "config.hpp"

#ifndef MOTORS_H
#define MOTORS_H

namespace bzzz
{   
    /**
     *
     */
    void writeSpeedToEsc(int rotor_speed_front_left, int rotor_speed_front_right, int rotor_speed_back_left, int rotor_speed_back_right);

    /**
     *
     */
    void disarm(void);

    /**
     *
     */
    void arm(void);

    /**
     *
     */
    bool getArmStatus(void);

}

#endif
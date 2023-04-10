#include "config.hpp"

#ifndef MOTORS_H
#define MOTORS_H

namespace bzzz
{

    /**
     *
     */
    void attachMotors(void);
    /**
     *
     */
    void writeSpeedToEsc(void);

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
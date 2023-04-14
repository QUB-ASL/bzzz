#include "config.hpp"

#ifndef MOTORS_H
#define MOTORS_H

namespace bzzz
{   
    /**
     * @brief Write the correct speed to correct motor(ESC_PIN)
     * 
     * @param rotor_speed_front_left set motor speed for FRONT_LEFT_ESC_PIN
     * @param rotor_speed_front_right set motor speed for FRONT_RIGHT_ESC_PIN
     * @param rotor_speed_back_left set motor speed for BACK_LEFT_ESC_PIN
     * @param rotor_speed_back_right set motor speed for BACK_RIGHT_ESC_PIN
     */
    void writeSpeedToEsc(int rotor_speed_front_left, int rotor_speed_front_right, int rotor_speed_back_left, int rotor_speed_back_right);

    /**
     * @brief disarm all motors
     */
    void disarm(void);

    /**
     * Arm all motors
     * Motor speed set to ARM_ROTOR_SPEED
     */
    void arm(void);

    /**
     * @brief Check if motors have been armed
     * 
     * @return true if motors are armed
     */
    bool getArmStatus(void);

}

#endif
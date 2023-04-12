
#include "motors.hpp"
#include "ESC.h"

namespace bzzz
{
    static bool s_armStatus = false;
    
    ESC frontLeftEsc(FRONT_LEFT_ESC_PIN, ABSOLUTE_MIN_PWM, ABSOLUTE_MAX_PWM, ARM_ROTOR_SPEED); // ESC_Name (PIN, Minimum Value, Maximum Value, Arm Value)
    ESC frontRightEsc(FRONT_RIGHT_ESC_PIN, ABSOLUTE_MIN_PWM, ABSOLUTE_MAX_PWM, ARM_ROTOR_SPEED);
    ESC backLeftEsc(BACK_LEFT_ESC_PIN, ABSOLUTE_MIN_PWM, ABSOLUTE_MAX_PWM, ARM_ROTOR_SPEED);
    ESC backRightEsc(BACK_RIGHT_ESC_PIN, ABSOLUTE_MIN_PWM, ABSOLUTE_MAX_PWM, ARM_ROTOR_SPEED);

    void writeSpeedToEsc(int rotor_speed_front_left, int rotor_speed_front_right, int rotor_speed_back_left, int rotor_speed_back_right)
    {
        frontLeftEsc.speed(rotor_speed_front_left); // sets the ESC speed  
        frontRightEsc.speed(rotor_speed_front_right); // sets the ESC speed
        backLeftEsc.speed(rotor_speed_back_left); // sets the ESC speed
        backRightEsc.speed(rotor_speed_back_right); // sets the ESC speed
    };

    void disarm(void)
    {
        bzzz::s_armStatus = 0;
        frontLeftEsc.stop(); // Send the Stop command to ESC  
        frontRightEsc.stop(); // Send the Stop command to ESC
        backLeftEsc.stop(); // Send the Stop command to ESC
        backRightEsc.stop(); // Send the Stop command to ESC
    };

    void arm(void)
    {
        bzzz::s_armStatus = 1;
        frontLeftEsc.arm(); // Send the Arm command to ESC  
        frontRightEsc.arm(); // Send the Arm command to ESC
        backLeftEsc.arm(); // Send the Arm command to ESC
        backRightEsc.arm(); // Send the Arm command to ESC
    };

    bool getArmStatus(void)
    {
        return bzzz::s_armStatus;
    };

}
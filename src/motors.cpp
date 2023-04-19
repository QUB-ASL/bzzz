#include "motors.hpp"

namespace bzzz
{

    TorqueSystem::TorqueSystem(){
        m_frontLeftEsc = new ESC(FRONT_LEFT_ESC_PIN, ABSOLUTE_MIN_PWM, ABSOLUTE_MAX_PWM, ARM_ROTOR_SPEED);
        m_frontRightEsc = new ESC(FRONT_RIGHT_ESC_PIN, ABSOLUTE_MIN_PWM, ABSOLUTE_MAX_PWM, ARM_ROTOR_SPEED);
        m_backLeftEsc = new ESC(BACK_LEFT_ESC_PIN, ABSOLUTE_MIN_PWM, ABSOLUTE_MAX_PWM, ARM_ROTOR_SPEED);
        m_backRightEsc = new ESC(BACK_RIGHT_ESC_PIN, ABSOLUTE_MIN_PWM, ABSOLUTE_MAX_PWM, ARM_ROTOR_SPEED);
    };

    void TorqueSystem::writeSpeedToEsc(int rotor_speed_front_left, int rotor_speed_front_right, int rotor_speed_back_left, int rotor_speed_back_right)
    {
        m_frontLeftEsc->speed(rotor_speed_front_left); // sets the ESC speed  
        m_frontRightEsc->speed(rotor_speed_front_right); // sets the ESC speed
        m_backLeftEsc->speed(rotor_speed_back_left); // sets the ESC speed
        m_backRightEsc->speed(rotor_speed_back_right); // sets the ESC speed
    };

    void TorqueSystem::disarm(void)
    {
        m_armStatus = 0;
        m_frontLeftEsc->stop(); // Send the Stop command to ESC  
        m_frontRightEsc->stop(); // Send the Stop command to ESC
        m_backLeftEsc->stop(); // Send the Stop command to ESC
        m_backRightEsc->stop(); // Send the Stop command to ESC
    };

    void TorqueSystem::arm(void)
    {
        m_armStatus = 1;
        m_frontLeftEsc->arm(); // Send the Arm command to ESC  
        m_frontRightEsc->arm(); // Send the Arm command to ESC
        m_backLeftEsc->arm(); // Send the Arm command to ESC
        m_backRightEsc->arm(); // Send the Arm command to ESC
    };

    bool TorqueSystem::getArmStatus(void)
    {
        return m_armStatus;
    };

}
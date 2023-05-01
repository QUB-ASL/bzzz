#include "motors.hpp"

namespace bzzz
{

    MotorDriver::MotorDriver(){};

    void MotorDriver::attachEscToPwmPin(void)
    {
        m_frontLeftEsc.attach(FRONT_LEFT_ESC_PIN, -1, 0, 180, ABSOLUTE_MIN_PWM, ABSOLUTE_MAX_PWM);
        m_frontRightEsc.attach(FRONT_RIGHT_ESC_PIN, -1, 0, 180, ABSOLUTE_MIN_PWM, ABSOLUTE_MAX_PWM);
        m_backLeftEsc.attach(BACK_LEFT_ESC_PIN, -1, 0, 180, ABSOLUTE_MIN_PWM, ABSOLUTE_MAX_PWM);
        m_backRightEsc.attach(BACK_RIGHT_ESC_PIN, -1, 0, 180, ABSOLUTE_MIN_PWM, ABSOLUTE_MAX_PWM);
    }

    void MotorDriver::writeSpeedToEsc(int rotorSpeedFrontLeft, int rotorSpeedFrontRight,
                                      int rotorSpeedBackLeft, int rotorSpeedBackRight)
    {
        m_frontLeftEsc.writeMicroseconds(rotorSpeedFrontLeft);   // sets the ESC speed
        m_frontRightEsc.writeMicroseconds(rotorSpeedFrontRight); // sets the ESC speed
        m_backLeftEsc.writeMicroseconds(rotorSpeedBackLeft);     // sets the ESC speed
        m_backRightEsc.writeMicroseconds(rotorSpeedBackRight);   // sets the ESC speed
    };

    void MotorDriver::disarm(void)
    {
        m_armStatus = 0;
        m_frontLeftEsc.writeMicroseconds(ZERO_ROTOR_SPEED);  // stop the motors. sets the ESC speed to ZERO_ROTOR_SPEED
        m_frontRightEsc.writeMicroseconds(ZERO_ROTOR_SPEED); // stop the motors. sets the ESC speed to ZERO_ROTOR_SPEED
        m_backLeftEsc.writeMicroseconds(ZERO_ROTOR_SPEED);   // stop the motors. sets the ESC speed to ZERO_ROTOR_SPEED
        m_backRightEsc.writeMicroseconds(ZERO_ROTOR_SPEED);  // stop the motors. sets the ESC speed to ZERO_ROTOR_SPEED
    };

    void MotorDriver::arm(void)
    {
        m_armStatus = 1;
        m_frontLeftEsc.writeMicroseconds(ARM_ROTOR_SPEED);  // start the motors. sets the ESC speed to IDLE_ROTOR_SPEED
        m_frontRightEsc.writeMicroseconds(ARM_ROTOR_SPEED); // start the motors. sets the ESC speed to IDLE_ROTOR_SPEED
        m_backLeftEsc.writeMicroseconds(ARM_ROTOR_SPEED);   // start the motors. sets the ESC speed to IDLE_ROTOR_SPEED
        m_backRightEsc.writeMicroseconds(ARM_ROTOR_SPEED);  // start the motors. sets the ESC speed to IDLE_ROTOR_SPEED
    };

    bool MotorDriver::getArmStatus(void)
    {
        return m_armStatus;
    };

}
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
        
#if UAV_TYPE == UAV_TYPE_HEXACOPTER
        m_midLeftEsc.attach(MID_LEFT_ESC_PIN, -1, 0, 180, ABSOLUTE_MIN_PWM, ABSOLUTE_MAX_PWM);
        m_midRightEsc.attach(MID_RIGHT_ESC_PIN, -1, 0, 180, ABSOLUTE_MIN_PWM, ABSOLUTE_MAX_PWM);
#endif
    }

#if UAV_TYPE == UAV_TYPE_QUADCOPTER
    void MotorDriver::writeSpeedToEsc(int rotorSpeedFrontLeft, int rotorSpeedFrontRight,
                                      int rotorSpeedBackLeft, int rotorSpeedBackRight,
                                      int minSpeed)
    {   
        m_frontLeftEsc.writeMicroseconds(max(minSpeed, rotorSpeedFrontLeft));   // sets the ESC speed
        m_frontRightEsc.writeMicroseconds(max(minSpeed, rotorSpeedFrontRight)); // sets the ESC speed
        m_backLeftEsc.writeMicroseconds(max(minSpeed, rotorSpeedBackLeft));     // sets the ESC speed
        m_backRightEsc.writeMicroseconds(max(minSpeed, rotorSpeedBackRight));   // sets the ESC speed
    }
#elif UAV_TYPE == UAV_TYPE_HEXACOPTER
    void MotorDriver::writeSpeedToEsc(int rotorSpeedFrontLeft, int rotorSpeedFrontRight,
                                      int rotorSpeedBackLeft, int rotorSpeedBackRight,
                                      int rotorSpeedMidLeft, int rotorSpeedMidRight,
                                      int minSpeed)

     

    { 



        m_frontLeftEsc.writeMicroseconds(max(minSpeed, rotorSpeedFrontLeft));   // sets the ESC speed
        m_frontRightEsc.writeMicroseconds(max(minSpeed, rotorSpeedFrontRight)); // sets the ESC speed
        m_backLeftEsc.writeMicroseconds(max(minSpeed, rotorSpeedBackLeft));     // sets the ESC speed
        m_backRightEsc.writeMicroseconds(max(minSpeed, rotorSpeedBackRight));   // sets the ESC speed
        m_midLeftEsc.writeMicroseconds(max(minSpeed, rotorSpeedMidLeft));       // sets the ESC speed
        m_midRightEsc.writeMicroseconds(max(minSpeed, rotorSpeedMidRight));     // sets the ESC speed


    }

   
#endif

    void MotorDriver::disarm(void)
    {
        // Serial.println("DISARM");
        m_armStatus = 0;
        m_frontLeftEsc.writeMicroseconds(ZERO_ROTOR_SPEED);  // stop the motors
        m_frontRightEsc.writeMicroseconds(ZERO_ROTOR_SPEED); // stop the motors
        m_backLeftEsc.writeMicroseconds(ZERO_ROTOR_SPEED);   // stop the motors
        m_backRightEsc.writeMicroseconds(ZERO_ROTOR_SPEED);  // stop the motors
        
#if UAV_TYPE == UAV_TYPE_HEXACOPTER
        m_midLeftEsc.writeMicroseconds(ZERO_ROTOR_SPEED);    // stop the motors
        m_midRightEsc.writeMicroseconds(ZERO_ROTOR_SPEED);   // stop the motors
#endif
    }
    


    void MotorDriver::arm(void)
    {
        m_armStatus = 1;
        m_frontLeftEsc.writeMicroseconds(ARM_ROTOR_SPEED);
        m_frontRightEsc.writeMicroseconds(ARM_ROTOR_SPEED);
        m_backLeftEsc.writeMicroseconds(ARM_ROTOR_SPEED);
        m_backRightEsc.writeMicroseconds(ARM_ROTOR_SPEED);
        
#if UAV_TYPE == UAV_TYPE_HEXACOPTER
        m_midLeftEsc.writeMicroseconds(ARM_ROTOR_SPEED);
        m_midRightEsc.writeMicroseconds(ARM_ROTOR_SPEED);
#endif
        delay(20);
    }

    bool MotorDriver::getArmStatus(void)
    {
        return m_armStatus;
    }

    void MotorDriver::attachAndArm()
    {
        attachEscToPwmPin();
        delay(3000);
        arm();
        delay(3000);
       
        
    }

    // void MotorDriver::motorTestSequence()
    // {
   

    //     m_frontLeftEsc.writeMicroseconds(1350);
    //     Serial.println("fml");
    //     delay(3000);
    //     m_frontLeftEsc.writeMicroseconds(900);
    //     delay(3000);
    //     m_frontRightEsc.writeMicroseconds(1350);
    //     Serial.println("fmr");
    //     delay(3000);
    //     m_frontRightEsc.writeMicroseconds(900);
    //     delay(3000);
    //     m_midRightEsc.writeMicroseconds(1350);
    //     Serial.println("mmr");
    //     delay(3000);
    //     m_midRightEsc.writeMicroseconds(900);
    //     delay(3000);
    //     m_backRightEsc.writeMicroseconds(1350);
    //     Serial.println("bmr");
    //     delay(3000);
    //     m_backRightEsc.writeMicroseconds(900);
    //     delay(3000);
    //     m_backLeftEsc.writeMicroseconds(1350);
    //     Serial.println("bml");
    //     delay(3000);
    //     m_backLeftEsc.writeMicroseconds(900);
    //     delay(3000);
    //     m_midLeftEsc.writeMicroseconds(1350);
    //     Serial.println("mml");
    //     delay(3000);
    //     m_midLeftEsc.writeMicroseconds(900);
    //     delay(900);



    // }

} /* end of namespace bzzz */
#include <Arduino.h>
#include "config.hpp"
#include "motors.hpp"
#include "radio.hpp"

bzzz::MotorDriver motorDriver;
bzzz::Radio radio;

void setup()
{
  motorDriver.attachAndArm();     // attach ESC and arm motors
} 


//HARDWARE TEST STOP START MOTORS

// void loop()
// {
//   motorDriver.writeSpeedToEsc(1150, 1150, 1150, 1150); // sets the ESC speed
//   delay(1000);                                         // Wait for a while 
//   motorDriver.disarm();                                // Stop the ESC altogether
//   delay(1000); 
// }


//HARDWARE TEST VARIABLE MOTOR SPEEDS

#define PERIOD 10000. // Period milliseconds

void loop()
{
  for (float i = 0; i < PERIOD; i++)
  {
    int commonMotorSpeed = ((ABSOLUTE_MAX_PWM - ZERO_ROTOR_SPEED)/2) 
                           * (sin(2.*PI*i*(1/PERIOD))+1) + ZERO_ROTOR_SPEED;
    motorDriver.writeSpeedToEsc(commonMotorSpeed, commonMotorSpeed, 
                                commonMotorSpeed, commonMotorSpeed);
    delay(1);         // Wait for a while
    if (i == PERIOD)
    {
      i=0;
    }
  }
}
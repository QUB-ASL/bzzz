#include <Arduino.h>
#include <config.hpp>
#include <motors.hpp>

bzzz::MotorDriver motorDriver;

void setup()
{
    motorDriver.attachAndArm(); // attach and arm the motors
}

#define PERIOD 1000. // Period milliseconds

void loop()
{
 for (float i = 0; i < PERIOD; i++)
 {
    int commonMotorSpeed = min(2000, int( 1000 + 0.1*i ) );
    motorDriver.writeSpeedToEsc(commonMotorSpeed, commonMotorSpeed,
                                commonMotorSpeed, commonMotorSpeed);
    delay(1); // Wait for a while
    if (i == PERIOD)
    {
        i = 0;
    }
 }
}
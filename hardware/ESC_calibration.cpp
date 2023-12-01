#include <Arduino.h>
#include "motors.hpp"
 
bzzz::MotorDriver motorDriver;
#define PERIOD_1 5000.
void setup()
{
    motorDriver.attachEscToPwmPin();
    motorDriver.writeSpeedToEsc(2000, 2000, 2000, 2000);
    delay(PERIOD_1);
    motorDriver.writeSpeedToEsc(1000, 1000, 1000, 1000);
    delay(PERIOD_1);
}
 
 
void loop()
{
 
}

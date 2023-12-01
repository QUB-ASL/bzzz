
#include <Arduino.h>
#include "motors.hpp"
 
bzzz::MotorDriver motorDriver;
// sets the delay value to 5 sec
#define PERIOD_1 5000. 
void setup()
{
    motorDriver.attachEscToPwmPin();
    motorDriver.writeSpeedToEsc(2000, 2000, 2000, 2000); // Sets the signal to ESC as high
    delay(PERIOD_1);
    motorDriver.writeSpeedToEsc(1000, 1000, 1000, 1000); // Sets the signal to ESC as low
    delay(PERIOD_1);
}
 
 
void loop()
{
 
}

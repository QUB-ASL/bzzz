
#include <Arduino.h>
#include "motors.hpp"
 
bzzz::MotorDriver motorDriver;
// sets the delay value to 5 sec
#define DELAY_BETWEEN_HIGH_LOW_SIGNALS 5000.
// Defining the signal high parameter
#define High_Sgn 2000.
// Defining the signal low parameter
#define Low_Sgn 1000.
void setup()
{
    motorDriver.attachEscToPwmPin();
    motorDriver.writeSpeedToEsc(High_Sgn, High_Sgn, High_Sgn, High_Sgn); // Sets the signal to ESC as high
    delay(DELAY_BETWEEN_HIGH_LOW_SIGNALS);
    motorDriver.writeSpeedToEsc(Low_Sgn, Low_Sgn, Low_Sgn, Low_Sgn); // Sets the signal to ESC as low
    delay(DELAY_BETWEEN_HIGH_LOW_SIGNALS);
}
 
 
void loop()
{
 
}

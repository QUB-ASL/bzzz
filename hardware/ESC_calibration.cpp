#include <Arduino.h>
#include "motors.hpp"
 
bzzz::MotorDriver motorDriver;
// sets the delay value to 5 sec
#define DELAY_BETWEEN_HIGH_LOW_SIGNALS 5000.
// Defining the signal high parameter
#define HIGH_SGN 2000.
// Defining the signal low parameter
#define LOW_SGN 1000.
void setup()
{
    motorDriver.attachEscToPwmPin();
    motorDriver.writeSpeedToEsc(HIGH_SGN, HIGH_SGN, HIGH_SGN, HIGH_SGN); // Sets the signal to ESC as high
    delay(DELAY_BETWEEN_HIGH_LOW_SIGNALS);
    motorDriver.writeSpeedToEsc(LOW_SGN, LOW_SGN, LOW_SGN, LOW_SGN); // Sets the signal to ESC as low
    delay(DELAY_BETWEEN_HIGH_LOW_SIGNALS);
}
 
 
void loop()
{
 
}

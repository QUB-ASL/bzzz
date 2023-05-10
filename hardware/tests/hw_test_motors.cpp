#include <Arduino.h>
#include "config.hpp"
#include "motors.hpp"
#include "radio.hpp"

bzzz::MotorDriver motorDriver;
bzzz::Radio radio;

void setup()
{
  Serial.begin(115200);
  delay(1500);
  motorDriver.attachEscToPwmPin();
  delay(1500);
  motorDriver.arm(); // arm the motors
  delay(5000);       // Note that RC_ESC recommends a delay of 5000 ms after arming
} 

void loop()
{
  motorDriver.writeSpeedToEsc(1150, 1150, 1150, 1150); // sets the ESC speed
  delay(1000);                                         // Wait for a while 
  motorDriver.disarm();                                // Stop the ESC altogether
  delay(1000); 
}
#include <Arduino.h>
#include "config.hpp"
#include "motors.hpp"
#include "radio.hpp"

bzzz::MotorDriver torqueSystem;
bzzz::Radio radio;

void setup()
{
  Serial.begin(115200);
  delay(1000);
  radio.readPiData();
  delay(100);
  while (!radio.armed())
   {
        radio.readPiData();
   }
  torqueSystem.attachEscToPwmPin();
  torqueSystem.arm();
  delay(3000); // Wait a while
} // speed will now jump to pot setting

void loop()
{
  if (radio.kill()) 
  {
      //Disarm motors then check if if kill switch is on or off
      torqueSystem.disarm();
      while(radio.kill())
      {
        radio.readKillSwitch();
      }
  }
  radio.readPiData();
  torqueSystem.writeSpeedToEsc(1150, 1150, 1150, 1150); // sets the ESC speed
}

/*
* HARDWARE TEST FOR MOTORS CONTROLLED BY THROTTLE
*
*void loop()
*{
*    if (radio.kill()) 
*    {
*      //Disarm motors then check if if kill switch is on or off
*      torqueSystem.disarm();
*      while(radio.kill())
*      {
*        radio.readKillSwitch();
*      }
*    }
*  radio.readPiData();
*  float throttlePrcntg = radio.throttleReferencePercentage();
*  int throttleToMotors = int (throttlePrcntg * (ABSOLUTE_MAX_PWM-ABSOLUTE_MIN_PWM) + ABSOLUTE_MIN_PWM);
*  //bzzz::logSerial(bzzz::LogVerbosityLevel::Severe, "throttlePrcntg = %f\n", throttlePrcntg);
*  torqueSystem.writeSpeedToEsc(throttleToMotors, throttleToMotors, throttleToMotors, throttleToMotors);
*  // delay(10);         // Wait for a while
*  
*}
*/
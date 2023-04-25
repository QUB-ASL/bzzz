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
  torqueSystem.arm();
  delay(1000); // Wait a while

  // // the following loop turns on the motor slowly, so get ready
  for (int commonMotorSpeed = 840; commonMotorSpeed < 1190; commonMotorSpeed++)
  {
    torqueSystem.writeSpeedToEsc(
        commonMotorSpeed, commonMotorSpeed, commonMotorSpeed, commonMotorSpeed);
    delay(10);
  }
} // speed will now jump to pot setting

void loop()
{
  torqueSystem.writeSpeedToEsc(1150, 1150, 1150, 1150); // sets the ESC speed
  delay(10);         // Wait for a while
}

/*
* HARDWARE TEST FOR MOTORS CONTROLLED BY THROTTLE
*
*void loop()
*{
*  radio.readPiData();
*  float throttlePrcntg = radio.throttleReferencePercentage();
*  int throttleToMotors = int (throttlePrcntg * 2000);
*  bzzz::logSerial(bzzz::LogVerbosityLevel::Severe, "throttlePrcntg = %f\n", throttlePrcntg);
*  torqueSystem.writeSpeedToEsc(throttleToMotors, throttleToMotors, throttleToMotors, throttleToMotors);
*  // delay(10);         // Wait for a while
*  
*}
*/
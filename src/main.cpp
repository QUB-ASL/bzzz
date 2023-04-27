#include <Arduino.h>
#include "config.hpp"
#include "motors.hpp"
#include "radio.hpp"

bzzz::TorqueSystem torqueSystem;
bzzz::Radio radio;


// Note: the following speeds may need to be modified for your particular hardware.
#define MIN_SPEED 1040 // speed just slow enough to turn motor off
#define MAX_SPEED 1240 // speed where my motor drew 3.6 amps at 12v.

long int val; // variable to read the value from the analog pin

void setup()
{
  Serial.begin(115200);
  radio.beginSerial(115200);
  delay(1000);
  torqueSystem.arm();
  delay(1000); // Wait a while

  // // the following loop turns on the motor slowly, so get ready
  for (int i = 0; i < 500; i++)
  {                                   
    // run speed from 840 to 1190
    int commonMotorSpeed = MIN_SPEED - 200 + i;
    // motor starts up about half way through loop
    torqueSystem.writeSpeedToEsc(
      commonMotorSpeed, commonMotorSpeed, commonMotorSpeed, commonMotorSpeed);  
    delay(20);
  }
} // speed will now jump to pot setting

void loop()
{
  radio.readPiData();
  float throttlePrcntg = radio.throttleReferencePercentage();
  int throttleToMotors = int (throttlePrcntg * 2000);
  bzzz::logSerial(bzzz::LogVerbosityLevel::Severe, "throttlePrcntg = %f\n", throttlePrcntg);
  torqueSystem.writeSpeedToEsc(throttleToMotors, throttleToMotors, throttleToMotors, throttleToMotors);
  // delay(10);         // Wait for a while
}

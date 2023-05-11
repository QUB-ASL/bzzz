#include <Arduino.h>
#include "config.hpp"
#include "motors.hpp"
#include "radio.hpp"
#include "util.hpp"

using namespace bzzz;

bzzz::MotorDriver motorDriver;
bzzz::Radio radio;

void setup()
{
  setupBuzzer();                  // setup the buzzer
  Serial.begin(SERIAL_BAUD_RATE); // start the serial
  buzz(2);                        // 2 beeps => AHRS setup complete
  waitForPiSerial();              // wait for the RPi and the RC to connect
  buzz(4);                        // 4 beeps => RPi+RC connected
  radio.waitForArmCommand();      // wait for the RC to send an arming command
  buzz(2, 400);                   // two long beeps => preparation for arming
  motorDriver.attachAndArm();     // attach ESC and arm motors
  buzz(6);                        // 6 beeps => motors armed; keep clear!
}

//HARDWARE TEST FOR ARM AND KILL WHEN MOTORS CONTROLLED BY THROTTLE

void loop()
{
  radio.readPiData();

  if (radio.kill())
  {
    motorDriver.disarm();
    return; // exit the loop
  }

  float throttlePrcntg = radio.throttleReferencePercentage();
  int throttleToMotors = int (throttlePrcntg * (ABSOLUTE_MAX_PWM - ZERO_ROTOR_SPEED) + ZERO_ROTOR_SPEED);
  //bzzz::logSerial(bzzz::LogVerbosityLevel::Severe, "throttlePrcntg = %f\n", throttlePrcntg);
  motorDriver.writeSpeedToEsc(throttleToMotors, throttleToMotors, throttleToMotors, throttleToMotors);
  // delay(10);         // Wait for a while
}
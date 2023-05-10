#include <Arduino.h>
#include "config.hpp"
#include "motors.hpp"
#include "radio.hpp"

bzzz::MotorDriver motorDriver;
bzzz::Radio radio;

void setupMotors()
{
  delay(1500);
  motorDriver.attachEscToPwmPin();
  delay(1500);
  motorDriver.arm(); // arm the motors
  delay(5000);       // Note that RC_ESC recommends a delay of 5000 ms after arming
}

void setup()
{
  Serial.begin(SERIAL_BAUD_RATE); // start the serial
  setupMotors();                  // attach ESC and arm motors
} 

//HARDWARE TEST FOR MOTORS CONTROLLED BY THROTTLE

void loop()
{
  radio.readPiData();
  float throttlePrcntg = radio.throttleReferencePercentage();
  int throttleToMotors = int (throttlePrcntg * (ABSOLUTE_MAX_PWM - ZERO_ROTOR_SPEED) + ZERO_ROTOR_SPEED);
  //bzzz::logSerial(bzzz::LogVerbosityLevel::Severe, "throttlePrcntg = %f\n", throttlePrcntg);
  motorDriver.writeSpeedToEsc(throttleToMotors, throttleToMotors, throttleToMotors, throttleToMotors);
  // delay(10);         // Wait for a while
}
#include <Arduino.h>
#include "config.hpp"
#include "motors.hpp"
#include "radio.hpp"

bzzz::MotorDriver motorDriver;
bzzz::Radio radio;

/**
 * Setup the buzzer
 */
void setupBuzzer()
{
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW); // turn off the buzzer
}

/**
 * Make bzzz's buzzer beep
 *
 * This will produce `numBeeps` beeps of duration
 * `durationMs` (in milliseconds) with equal pauses
 * between the beeps.
 *
 * @param numBeeps number of beeps
 * @param durationMs duration of every beep in ms
 */
void buzz(int numBeeps = 4, int durationMs = 50)
{
  for (int i = 0; i < numBeeps; i++)
  {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(durationMs);
    digitalWrite(BUZZER_PIN, LOW);
    delay(durationMs);
  }
}

/**
 * Wait until Raspberry Pi sends some data
 */
void waitForPiSerial()
{
  while (!Serial.available())
  {
    // just wait
  }
}

/**
 * Wait until the arm switch is at the ON position
 */
void waitForArmCommand()
{
  radio.readPiData();
  delay(1000);
  while (!radio.armed())
  {
    radio.readPiData();
  }
}

/**
 * Setup the motor driver: attach and arm
 */
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
  setupBuzzer();                  // setup the buzzer
  Serial.begin(SERIAL_BAUD_RATE); // start the serial
  buzz(2);                        // 2 beeps => AHRS setup complete
  waitForPiSerial();              // wait for the RPi and the RC to connect
  buzz(4);                        // 4 beeps => RPi+RC connected
  waitForArmCommand();            // wait for the RC to send an arming command
  buzz(2, 400);                   // two long beeps => preparation for arming
  setupMotors();                  // attach ESC and arm motors
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
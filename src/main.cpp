#include <Arduino.h>
#include "quaternion.hpp"
#include "config.hpp"
#include "motors.hpp"
#include "radio.hpp"
#include "ahrs.hpp"
#include "controller.hpp"
#include "util.hpp"

using namespace bzzz;

MotorDriver motorDriver;
Radio radio;
AHRS ahrs;
Controller controller;
Quaternion initialQuaternion;
float yawReferenceRad = 0.0;
float initialAngularVelocity[3];

/**
 * Setup the AHRS
 */
void setupAHRS()
{
  ahrs.setup();
  ahrs.preflightCalibrate(false);
  ahrs.calibrateMagnetometer(MAGNETOMETER_BIAS_X, MAGNETOMETER_BIAS_Y, MAGNETOMETER_BIAS_Z,
                             MAGNETOMETER_SCALE_X, MAGNETOMETER_SCALE_X, MAGNETOMETER_SCALE_X);
}

/**
 * Setup function
 */
void setup()
{
  setupBuzzer();                                         // setup the buzzer
  Serial.begin(SERIAL_BAUD_RATE);                        // start the serial
  setupAHRS();                                           // setup the IMU and AHRS
  ahrs.averageQuaternion(initialQuaternion);             // determine initial attitude
  ahrs.averageAngularVelocities(initialAngularVelocity); // determine initial attitude
  buzz(2);                                               // 2 beeps => AHRS setup complete
  Serial.println("waiting for PiSerial...");
  waitForPiSerial();                                     // wait for the RPi and the RC to connect
  buzz(4);                                               // 4 beeps => RPi+RC connected
  Serial.println("waiting for arm...");
  radio.waitForArmCommand();                             // wait for the RC to send an arming command
  Serial.println("armed...");
  buzz(2, 400);                                          // two long beeps => preparation for arming
  motorDriver.attachAndArm();                            // attach ESC and arm motors
  buzz(6);                                               // 6 beeps => motors armed; keep clear!
}

/**
 * Set controller gain values from RC trimmers
 */
void setGainsFromRcTrimmers()
{
  controller.setQuaternionGains(
      -radio.trimmerVRAPercentage() * RADIO_TRIMMER_MAX_QUATERNION_XY_GAIN,
      -radio.trimmerVRBPercentage() * RADIO_TRIMMER_MAX_QUATERNION_Z_GAIN);
  controller.setAngularVelocityGains(
      -radio.trimmerVRCPercentage() * RADIO_TRIMMER_MAX_OMEGA_XY_GAIN,
      -radio.trimmerVREPercentage() * RADIO_TRIMMER_MAX_OMEGA_Z_GAIN);
}

/**
 * Loop function
 */
void loop()
{
  float quaternionImuData[4];
  float measuredAngularVelocity[3];
  float angularVelocityCorrected[3];
  float controls[3];

  radio.readPiData();
  if (radio.kill())
  {
    motorDriver.disarm();
    return; // exit the loop
  }

  ahrs.update();
  setGainsFromRcTrimmers();
  ahrs.quaternion(quaternionImuData);
  ahrs.angularVelocity(measuredAngularVelocity);

  // Determine correct angularVelocity
  angularVelocityCorrected[0] = measuredAngularVelocity[0] - initialAngularVelocity[0];
  angularVelocityCorrected[1] = measuredAngularVelocity[1] - initialAngularVelocity[1];
  angularVelocityCorrected[2] = measuredAngularVelocity[2] - initialAngularVelocity[2];

  // !!!deactivate for testing!!!
  // yawReferenceRad += radio.yawRateReferenceRadSec() * SAMPLING_TIME;

  Quaternion referenceQuaternion(
      yawReferenceRad,
      radio.pitchReferenceAngleRad(),
      radio.rollReferenceAngleRad());

  Quaternion currentQuaternion(quaternionImuData);
  Quaternion relativeQuaternion = currentQuaternion - initialQuaternion;
  Quaternion attitudeError = referenceQuaternion - relativeQuaternion; // e = set point - measured

  Serial.println("Yr: " + String(radio.yawRateReferenceRadSec()) + " Pr: " + String(radio.pitchReferenceAngleRad()) + " Rr: " + String(radio.rollReferenceAngleRad()) + " Tr: " + String(radio.throttleReferencePercentage()));
  
  controller.controlAction(attitudeError, angularVelocityCorrected, controls);

  // Throttle from RC to throttle reference
  float throttlePrcntFromRc = radio.throttleReferencePercentage();
  float throttleRef = mapPrcnt(throttlePrcntFromRc, ZERO_ROTOR_SPEED, ABSOLUTE_MAX_PWM);

  // Compute control actions and send them to the motors
  int motorFL, motorFR, motorBL, motorBR;
  controller.motorPwmSignals(attitudeError,
                             angularVelocityCorrected,
                             throttleRef,
                             motorFL, motorFR, motorBL, motorBR);
  motorDriver.writeSpeedToEsc(motorFL, motorFR, motorBL, motorBR);
}

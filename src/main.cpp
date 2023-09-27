#include <Arduino.h>
#include "quaternion.hpp"
#include "config.hpp"
#include "motors.hpp"
#include "radio.hpp"
#include "ahrs.hpp"
#include "controller.hpp"
#include "fail_safes.hpp"
#include "util.hpp"

using namespace bzzz;

MotorDriver motorDriver;
Radio radio(true);
AHRS ahrs;
Controller controller;
Quaternion initialQuaternion;
FailSafes failSafes(TX_CONNECTION_TIMEOUT_IN_uS);
float yawReferenceRad = 0.0;
float initialAngularVelocity[3];
float IMUData[6];
int motorFL, motorFR, motorBL, motorBR;

/**
 * Setup the AHRS
 */
void setupAHRS()
{
  ahrs.setup();
  ahrs.preflightCalibrate(false);
  ahrs.calibrateMagnetometer(MAGNETOMETER_BIAS_X, MAGNETOMETER_BIAS_Y, MAGNETOMETER_BIAS_Z,
                             MAGNETOMETER_SCALE_X, MAGNETOMETER_SCALE_Y, MAGNETOMETER_SCALE_Z);
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
  logSerial(LogVerbosityLevel::Info, "waiting for PiSerial...");
  waitForPiSerial(); // wait for the RPi and the RC to connect
  buzz(4);           // 4 beeps => RPi+RC connected
  logSerial(LogVerbosityLevel::Info, "waiting for arm...");
  radio.waitForArmCommand(); // wait for the RC to send an arming command
  logSerial(LogVerbosityLevel::Info, "arming...");
  buzz(2, 400);               // two long beeps => preparation for arming
  motorDriver.attachAndArm(); // attach ESC and arm motors
  buzz(6);                    // 6 beeps => motors armed; keep clear!
}

/**
 * Set controller gain values from RC trimmers
 *
 * Trimmer A - X/Y quaternion gain
 * Trimmer B - X/Y angular velocity gain
 * Trimmer C - Yaw angular velocity gain
 */
void setGainsFromRcTrimmers()
{
  controller.setQuaternionGain(
      - QUATERNION_XY_GAIN * RADIO_TRIMMER_MAX_QUATERNION_XY_GAIN);
  controller.setAngularVelocityXYGain(
      - OMEGA_XY_GAIN * RADIO_TRIMMER_MAX_OMEGA_XY_GAIN);
  controller.setYawAngularVelocityGain(
      - OMEGA_Z_GAIN * RADIO_TRIMMER_MAX_OMEGA_Z_GAIN);
}

/**
 * Loop function
 */
void loop()
{
  float quaternionImuData[4];
  float measuredAngularVelocity[3];
  float angularVelocityCorrected[3];

  // if radio data received update the last data read time.
  if (radio.readPiData())
  {
    radio.sendFlightDataToPi(IMUData[0], IMUData[1], IMUData[2], IMUData[3], IMUData[4], IMUData[5], motorFL, motorFR, motorBL, motorBR);
    failSafes.setLastRadioReceptionTime(micros());
  }
  // one function to run all fail safe checks
  if (radio.kill() || failSafes.isSerialTimeout())
  {
    motorDriver.disarm();
    logSerial(LogVerbosityLevel::Debug, "Exit loop!");
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

  float yawRateRC = radio.yawRateReferenceRadSec();
  float deadZoneYawRate = 0.017;
  float yawRateReference = 0.;
  if (yawRateRC >= deadZoneYawRate)
  {
    yawRateReference = yawRateRC - deadZoneYawRate;
  }
  else if (yawRateRC <= -deadZoneYawRate)
  {
    yawRateReference = yawRateRC + deadZoneYawRate;
  }

  // take the current Yaw angle as reference, this means that we are not correcting the Yaw.
  yawReferenceRad = ahrs.currentYawRad();

  Quaternion referenceQuaternion(
      yawReferenceRad,
      radio.pitchReferenceAngleRad(),
      radio.rollReferenceAngleRad());

  Quaternion currentQuaternion(quaternionImuData);
  Quaternion relativeQuaternion = currentQuaternion - initialQuaternion;
  Quaternion attitudeError = referenceQuaternion - relativeQuaternion; // e = set point - measured

  IMUData[0] = relativeQuaternion[1];
  IMUData[1] = relativeQuaternion[2];
  IMUData[2] = relativeQuaternion[3];
  ahrs.getAccelerometerValues(IMUData + 3);

  // Throttle from RC to throttle reference
  float throttleRef = radio.throttleReferencePWM();

  // Compute control actions and send them to the motors
  controller.motorPwmSignals(attitudeError,
                             angularVelocityCorrected,
                             yawRateReference,
                             throttleRef,
                             motorFL, motorFR, motorBL, motorBR);
  motorDriver.writeSpeedToEsc(motorFL, motorFR, motorBL, motorBR);

  logSerial(LogVerbosityLevel::Debug, "PR: %f %f\n",
            IMUData[1], IMUData[2]);
}

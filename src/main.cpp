#include <Arduino.h>
#include "quaternion.hpp"
#include "config.hpp"
#include "motors.hpp"
#include "radio.hpp"
#include "ahrs.hpp"
#include "controller.hpp"

using namespace bzzz;

MotorDriver motorDriver;
Radio radio;
AHRS ahrs;
Controller controller;
Quaternion initialQuaternion;
float yawReferenceRad = 0.0;
float initialAngularVelocity[3];

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
 * Setup the motor driver (and warm up the engine, by spinning the
 * motors a bit)
 */
void setupMotors()
{
  delay(1500);
  motorDriver.attachEscToPwmPin();
  delay(1500);
  motorDriver.arm();
  delay(1500);
  buzz(6);
}

/**
 * At the beginning the AHRS hasn't converged, so we need to discard
 * some measurements
 */
void discardImuMeasurements(size_t numMeasurements = 5000)
{
  for (int i = 0; i < numMeasurements; i++)
  {
    ahrs.update();
  }
}

/**
 * Determine the initial angular velocity readings of the IMU. 
 * This value is subtracted from the angular velocity readings of the IMU
 * to get the correct angular velocity. 
 * All angular velocities should be zero (at the start) when quadrotor is still.
 */
void initAngularVelocity()
{
  float AngularVelocityTemp[3] = {0};
  float AngularVelocityAverage[3] = {0};
  int numInitAngularVelocity = 10;

  for (int i = 0; i < numInitAngularVelocity; i++)
  {
    ahrs.update();
    ahrs.angularVelocity(AngularVelocityTemp);
    AngularVelocityAverage[0] += AngularVelocityTemp[0];
    AngularVelocityAverage[1] += AngularVelocityTemp[1];
    AngularVelocityAverage[2] += AngularVelocityTemp[2];
  }
  AngularVelocityAverage[0] /= (float)numInitAngularVelocity;
  AngularVelocityAverage[1] /= (float)numInitAngularVelocity;
  AngularVelocityAverage[2] /= (float)numInitAngularVelocity;

  initialAngularVelocity[0] = AngularVelocityAverage[0];
  initialAngularVelocity[1] = AngularVelocityAverage[1];
  initialAngularVelocity[2] = AngularVelocityAverage[2];
}

/**
 * Determine the initial attitude of the quadcopter. The initial
 * quaternion is stored in `initialQuaternion`.
 */
void initAttitude()
{
  float quatInitTemp[4] = {0};
  float averageQuaternion[4] = {0}; // 3D quaternion (x, y, z)
  int numInitQUat = 10;

  // make sure the estimator has converged; discard initial measurements
  logSerial(LogVerbosityLevel::Info, "[AHRS] getting ready; discarding measurements");
  discardImuMeasurements(10000);

  for (int i = 0; i < numInitQUat; i++)
  {
    ahrs.update();
    ahrs.quaternion(quatInitTemp);
    averageQuaternion[0] += quatInitTemp[0];
    averageQuaternion[1] += quatInitTemp[1];
    averageQuaternion[2] += quatInitTemp[2];
    averageQuaternion[3] += quatInitTemp[3];
  }
  averageQuaternion[0] /= (float)numInitQUat;
  averageQuaternion[1] /= (float)numInitQUat;
  averageQuaternion[2] /= (float)numInitQUat;
  averageQuaternion[3] /= (float)numInitQUat;

  float normAverageQuaternion =
      sqrt(sq(averageQuaternion[0]) + sq(averageQuaternion[1]) + sq(averageQuaternion[2]) + sq(averageQuaternion[3]));

  initialQuaternion[0] = averageQuaternion[0] / normAverageQuaternion;
  initialQuaternion[1] = averageQuaternion[1] / normAverageQuaternion;
  initialQuaternion[2] = averageQuaternion[2] / normAverageQuaternion;
  initialQuaternion[3] = averageQuaternion[3] / normAverageQuaternion;
}

/**
 * Setup the AHRS
 */
void setupAHRS()
{
  ahrs.setup();
  ahrs.preflightCalibrate(false);
  // TODO create #define's with these parameters
  ahrs.calibrateMagnetometer(222.566, 41.087, -60.268, 1.050, 0.936, 1.022);
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
 * Setup function
 */
void setup()
{
  setupBuzzer();
  Serial.begin(SERIAL_BAUD_RATE);
  setupAHRS();
  buzz(2);
  initAttitude();
  initAngularVelocity();
  buzz(3);
  delay(1000);
  buzz(3);
  waitForArmCommand();
  setupMotors();
}

void loop()
{
  float quaternionImuData[4];
  float measuredAngularVelocity[3];
  float angularVelocityCorrected[3];
  float controls[3];

  // Note:
  // Forward pitch, right roll and heading towards west must be positive

  radio.readPiData();

  if (radio.kill())
  {
    motorDriver.disarm();
    return; // exit the loop
  }

  ahrs.update();

  controller.setQuaternionGains(
      -radio.trimmerVRAPercentage() * 100.,
      -radio.trimmerVRBPercentage() * 20.);
  controller.setAngularVelocityGains(
      -radio.trimmerVRCPercentage() * 0.5,
      -radio.trimmerVREPercentage() * 0.05);

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

  controller.controlAction(attitudeError, angularVelocityCorrected, controls);

  // TODO Remove hard-coded numbers from here
  float throttleFromRadio = radio.throttleReferencePercentage() * 1000 + 1000;

  // Compute control actions and send them to the motors
  int motorFL, motorFR, motorBL, motorBR;
  controller.motorPwmSignals(attitudeError,
                             angularVelocityCorrected,
                             throttleFromRadio,
                             motorFL, motorFR, motorBL, motorBR);
  motorDriver.writeSpeedToEsc(motorFL, motorFR, motorBL, motorBR);

  // To print do:
  // logSerial(LogVerbosityLevel::Info,
  //           "%.3f\t %.3f\t %.3f\t %.3f",
  //           relativeQuaternion[0], relativeQuaternion[1], relativeQuaternion[2], relativeQuaternion[3]);
}

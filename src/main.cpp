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
float initialAngularVelocity[3] = {0.0};

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
  float angularVelocityTemp[3] = {0};
  float angularVelocityAverage[3] = {0};
  int numInitAngularVelocity = 10;

  for (int i = 0; i < numInitAngularVelocity; i++)
  {
    ahrs.update();
    ahrs.angularVelocity(angularVelocityTemp);
    angularVelocityAverage[0] += angularVelocityTemp[0];
    angularVelocityAverage[1] += angularVelocityTemp[1];
    angularVelocityAverage[2] += angularVelocityTemp[2];
  }
  angularVelocityAverage[0] /= (float)numInitAngularVelocity;
  angularVelocityAverage[1] /= (float)numInitAngularVelocity;
  angularVelocityAverage[2] /= (float)numInitAngularVelocity;

  initialAngularVelocity[0] = angularVelocityAverage[0];
  initialAngularVelocity[1] = angularVelocityAverage[1];
  initialAngularVelocity[2] = angularVelocityAverage[2];
}

/**
 * Determine the initial attitude of the quadcopter. The initial
 * quaternion is stored in `initialQuaternion`.
 */
void initAttitude()
{
  float quatInitTemp[4] = {0};
  float averageQuaternion3D[3] = {0}; // 3D quaternion (x, y, z)
  int numInitQUat = 10;

  // make sure the estimator has converged; discard initial measurements
  logSerial(LogVerbosityLevel::Info, "[AHRS] getting ready; discarding measurements");
  discardImuMeasurements(10000);

  for (int i = 0; i < numInitQUat; i++)
  {
    ahrs.update();
    ahrs.quaternion(quatInitTemp);
    averageQuaternion3D[0] += quatInitTemp[1];
    averageQuaternion3D[1] += quatInitTemp[2];
    averageQuaternion3D[2] += quatInitTemp[3];
  }
  averageQuaternion3D[0] /= (float)numInitQUat;
  averageQuaternion3D[1] /= (float)numInitQUat;
  averageQuaternion3D[2] /= (float)numInitQUat;

  float normSqAverageQuaternion3D =
      sq(averageQuaternion3D[0]) + sq(averageQuaternion3D[1]) + sq(averageQuaternion3D[2]);

  initialQuaternion[0] = sqrt(1. - normSqAverageQuaternion3D);
  initialQuaternion[1] = averageQuaternion3D[0];
  initialQuaternion[2] = averageQuaternion3D[1];
  initialQuaternion[3] = averageQuaternion3D[2];
}

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
  Serial.begin(SERIAL_BAUD_RATE);
  setupAHRS();
  initAttitude();
  initAngularVelocity();
  // The first time we read data from the radio, wait to make sure a
  // connection has been established
  while (!radio.readPiData())
  {
    // just wait to receive data from the radio
  }
  delay(2000);
  while (!radio.armed())
  {
    radio.readPiData();
  }
  setupMotors();
}

void handleKill()
{
  if (radio.kill())
  {
    // Disarm motors then check if if kill switch is on or off
    motorDriver.disarm();
    while (radio.kill())
    {
      radio.readKillSwitch();
    }
  }
}

void updateGainsFromRC()
{
  controller.setQuaternionGains(
      -radio.trimmerVRAPercentage() * RADIO_TRIMMER_MAX_QUATERNION_XY_GAIN,
      -radio.trimmerVRBPercentage() * RADIO_TRIMMER_MAX_QUATERNION_Z_GAIN);
  controller.setAngularVelocityGains(
      -radio.trimmerVRCPercentage() * RADIO_TRIMMER_MAX_OMEGA_XY_GAIN,
      -radio.trimmerVREPercentage() * RADIO_TRIMMER_MAX_OMEGA_Z_GAIN);
}

void loop()
{
  float quaternionImuData[4];
  float angularVelocity[3];
  float angularVelocityCorrected[3];
  float controls[3];

  handleKill();
  updateGainsFromRC();

  ahrs.update();
  radio.readPiData();

  ahrs.quaternion(quaternionImuData);
  ahrs.angularVelocity(angularVelocity);

  // Determine correct angularVelocity
  angularVelocityCorrected[0] = angularVelocity[0] - initialAngularVelocity[0];
  angularVelocityCorrected[1] = angularVelocity[1] - initialAngularVelocity[1];
  angularVelocityCorrected[2] = angularVelocity[2] - initialAngularVelocity[2];

  // !!!deactivate for testing!!!
  // TODO Next, we should fix this
  // NOTE: It is very important that when the stick is at the middle,
  //       the raw rate is exactly zero
  // yawReferenceRad += radio.yawRateReferenceRadSec() * SAMPLING_TIME;

  // Read reference quaternion from RC
  Quaternion referenceQuaternion(
      yawReferenceRad,
      radio.pitchReferenceAngleRad(),
      radio.rollReferenceAngleRad());

  Quaternion currentQuaternion(quaternionImuData);
  Quaternion relativeQuaternion = currentQuaternion - initialQuaternion;
  Quaternion attitudeError = referenceQuaternion - relativeQuaternion; // e = set point - measured

  float throttleFromRadio = radio.throttleReferencePercentage() * (ABSOLUTE_MAX_PWM - ABSOLUTE_MIN_PWM) + ABSOLUTE_MIN_PWM;

  // control actions to the motors
  int motorFL, motorFR, motorBL, motorBR;

  controller.motorPwmSignals(attitudeError,
                             angularVelocityCorrected,
                             throttleFromRadio,
                             motorFL, motorFR, motorBL, motorBR);

  motorDriver.writeSpeedToEsc(motorFL, motorFR, motorBL, motorBR);

  // To print do:
  // logSerial(LogVerbosityLevel::Info,
  //          "%.3f\t %.3f\t %.3f\t %.3f\t %.3f\t %.3f",
  //          angularVelocity[0], angularVelocityCorrected[0],
  //          angularVelocity[1], angularVelocityCorrected[1],
  //          angularVelocity[2], angularVelocityCorrected[2]);
}

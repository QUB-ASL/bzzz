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

/**
 * Setup the motor driver (and warm up the engine, by spinning the
 * motors a bit)
 */
void setupMotors()
{
  delay(1000);
  motorDriver.arm();
  delay(1000);

  // the following loop turns on the motor slowly, so get ready
  for (int commonMotorSpeed = 840; commonMotorSpeed < 1190; commonMotorSpeed++)
  {
    motorDriver.writeSpeedToEsc(
        commonMotorSpeed, commonMotorSpeed, commonMotorSpeed, commonMotorSpeed);
    delay(20);
  }
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
 * Determine the initial attitude of the quadcopter. The initial
 * quaternion is stored in `initialQuaternion`.
 */
void initAttitude()
{
  float quatInitTemp[4] = {0};
  float averageQuaternion3D[3] = {0}; // 3D quaternion (x, y, z)
  int numInitQUat = 10;

  // make sure the estimator has converged
  // discard initial measurements
  logSerial(LogVerbosityLevel::Info, "[AHRS] getting ready; discaring measurements");
  discardImuMeasurements();

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
      sq(averageQuaternion3D[0]) - sq(averageQuaternion3D[1]) - sq(averageQuaternion3D[2]);
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
  ahrs.calibrateMagnetometer(222.566, 41.087, -60.268, 1.050, 0.936, 1.022);
}

/**
 * Setup function
 */
void setup()
{
  Serial.begin(SERIAL_BAUD_RATE);
  setupAHRS();
  setupMotors();
  initAttitude();
}

void loop()
{
  float quaternionImuData[4];
  float angularVelocity[3];
  float controls[3];

  /*  !!! NOTE !!! I commented this out to test things locally  */

  // controller.setQuaternionGains(
  //     -radio.trimmerVRAPercentage() * 30.,
  //     -radio.trimmerVRBPercentage() * 5.);
  // controller.setAngularVelocityGains(
  //     -radio.trimmerVRCPercentage() * 5.,
  //     -radio.trimmerVREPercentage() * 5.);

  ahrs.update();
  radio.readPiData();

  ahrs.quaternion(quaternionImuData);
  ahrs.angularVelocity(angularVelocity);

  yawReferenceRad += radio.yawRateReferenceRadSec() * SAMPLING_TIME;
  Quaternion referenceQuaternion;

  /*  !!! NOTE !!! I commented this out to test things locally  */
  // Quaternion referenceQuaternion(
  //     yawReferenceRad,
  //     radio.pitchReferenceAngleRad(),
  //     radio.rollReferenceAngleRad());

  Quaternion currentQuaternion(quaternionImuData);
  Quaternion relativeQuaternion = currentQuaternion - initialQuaternion;
  Quaternion attitudeError = relativeQuaternion - referenceQuaternion;

  controller.controlAction(attitudeError, angularVelocity, controls);

  // control actions to the motors
  float throttleFromRadio = radio.throttleReferencePercentage() * 1000 + 1000;
  float motorFL = throttleFromRadio + U_TO_PWM * (controls[0] + controls[1] + controls[2]);
  float motorFR = throttleFromRadio + U_TO_PWM * (-controls[0] + controls[1] - controls[2]);
  float motorBL = throttleFromRadio + U_TO_PWM * (controls[0] - controls[1] - controls[2]);
  float motorBR = throttleFromRadio + U_TO_PWM * (-controls[0] - controls[1] + controls[2]);

  motorDriver.writeSpeedToEsc(motorFL, motorFR, motorBL, motorBR);

  logSerial(LogVerbosityLevel::Info,
            "%.3f\t %.3f\t %.3f\t %.3f",
            attitudeError[0], attitudeError[1], attitudeError[2], attitudeError[3]);
}

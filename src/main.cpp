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
  motorDriver.arm();
  delay(1000);
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
  radio.readPiData();
  delay(2000);
      while (!radio.armed())
      {
          radio.readPiData();
      }
  setupMotors();
}

void loop()
{
  float quaternionImuData[4];
  float angularVelocity[3];
  float angularVelocityCorrected[3];
  float controls[3];

    if (radio.kill()) 
    {
      //Disarm motors then check if if kill switch is on or off
      motorDriver.disarm();
      while(radio.kill())
      {
        radio.readKillSwitch();
      }
    }

  // Note:
  // Forward pitch, left roll and heading towards west must be positive

  controller.setQuaternionGains(
      -radio.trimmerVRAPercentage() * 50.,
      -radio.trimmerVRBPercentage() * 10.);
  controller.setAngularVelocityGains(
      -radio.trimmerVRCPercentage() * 0.1,
      -radio.trimmerVREPercentage() * 0.1);

  ahrs.update();
  radio.readPiData();

  ahrs.quaternion(quaternionImuData);
  ahrs.angularVelocity(angularVelocity);

  // Determine correct angularVelocity
  angularVelocityCorrected[0] = angularVelocity[0] - initialAngularVelocity[0];
  angularVelocityCorrected[1] = angularVelocity[1] - initialAngularVelocity[1];
  angularVelocityCorrected[2] = angularVelocity[2] - initialAngularVelocity[2];

  // !!!deactivate for testing!!!
  //yawReferenceRad += radio.yawRateReferenceRadSec() * SAMPLING_TIME;

  // TODO Try to update the function radio.rollReferenceAngleRad() and add a minus
  Quaternion referenceQuaternion(
      yawReferenceRad,
      radio.pitchReferenceAngleRad(),
      radio.rollReferenceAngleRad());

  Quaternion currentQuaternion(quaternionImuData);
  Quaternion relativeQuaternion = currentQuaternion - initialQuaternion;
  Quaternion attitudeError = referenceQuaternion - relativeQuaternion; // e = set point - measured

  controller.controlAction(attitudeError, angularVelocityCorrected, controls);

  float throttleFromRadio = radio.throttleReferencePercentage() 
                            * (ABSOLUTE_MAX_PWM - ABSOLUTE_MIN_PWM) 
                            + ABSOLUTE_MIN_PWM;

  // TODO create a method (in Controller) like
  // void controller.motorSignals(
  //       float throttleReference,
  //       Quaternion& attitudeError,
  //       const float* angularVelocity,
  //       float* motorSignals);

  // control actions to the motors
  // THINK SOMETHING NOT QUITE RIGHT WITH motorFL.
  // THE QUATERNION GAIN SEEMS TO EFFECT IT MORE THAN THE OTHER MOTORS
  float motorFL = throttleFromRadio + U_TO_PWM * (controls[0] + controls[1] + controls[2]);
  float motorFR = throttleFromRadio + U_TO_PWM * (-controls[0] + controls[1] - controls[2]);
  float motorBL = throttleFromRadio + U_TO_PWM * (controls[0] - controls[1] - controls[2]);
  float motorBR = throttleFromRadio + U_TO_PWM * (-controls[0] - controls[1] + controls[2]);

  motorDriver.writeSpeedToEsc(motorFL, motorFR, motorBL, motorBR);

  // To print do:
  //logSerial(LogVerbosityLevel::Info,
  //          "%.3f\t %.3f\t %.3f\t %.3f\t %.3f\t %.3f", 
  //          angularVelocity[0], angularVelocityCorrected[0],
  //          angularVelocity[1], angularVelocityCorrected[1],
  //          angularVelocity[2], angularVelocityCorrected[2]);
}

#include <Arduino.h>
#include "quaternion.hpp"
#include "config.hpp"
#include "motors.hpp"
#include "radio.hpp"
#include "ahrs.hpp"
#include "controller.hpp"

using namespace bzzz;

TorqueSystem torqueSystem;
Radio radio;
AHRS ahrs;
Controller controller;
float yawReferenceRad = 0.0;

void setupMotors()
{
  delay(1000);
  torqueSystem.arm();
  delay(1000);

  // the following loop turns on the motor slowly, so get ready
  for (int commonMotorSpeed = 840; commonMotorSpeed < 1190; commonMotorSpeed++)
  {
    torqueSystem.writeSpeedToEsc(
        commonMotorSpeed, commonMotorSpeed, commonMotorSpeed, commonMotorSpeed);
    delay(20);
  }
}

void setup()
{
  Serial.begin(SERIAL_BAUD_RATE);
  ahrs.setup();
  setupMotors();
}

void loop()
{
  float quaternionImuData[4];
  float angularVelocity[3];
  float controls[3];

  ahrs.update();
  radio.readPiData();

  ahrs.quaternion(quaternionImuData);
  ahrs.angularVelocity(angularVelocity);

  yawReferenceRad += radio.yawRateReferenceRadSec() * SAMPLING_TIME;
  Quaternion referenceQuaternion(
      yawReferenceRad,
      radio.pitchReferenceAngleRad(),
      radio.rollReferenceAngleRad());

  Quaternion currentQuaternion(quaternionImuData);
  Quaternion attitudeError = currentQuaternion - referenceQuaternion;

  controller.controlAction(attitudeError, angularVelocity, controls);

  float throttleFromRadio = radio.throttleReferencePercentage() * 1000 + 1000;

  float motorFL = throttleFromRadio + U_TO_PWM * (controls[0] + controls[1] + controls[2]);
  float motorFR = throttleFromRadio + U_TO_PWM * (-controls[0] + controls[1] - controls[2]);
  float motorBL = throttleFromRadio + U_TO_PWM * (controls[0] - controls[1] - controls[2]);
  float motorBR = throttleFromRadio + U_TO_PWM * (-controls[0] - controls[1] + controls[2]);

  torqueSystem.writeSpeedToEsc(motorFL, motorFR, motorBL, motorBR);

  // bzzz::logSerial(bzzz::LogVerbosityLevel::Severe, "throttlePrcntg = %f\n", throttlePrcntg);
}

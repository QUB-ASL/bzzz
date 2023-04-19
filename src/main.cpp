#include <Arduino.h>
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

void setup()
{
  Serial.begin(SERIAL_BAUD_RATE);
  ahrs.setup();

  delay(1000);
  torqueSystem.arm();
  delay(1000); // Wait a while

  // // the following loop turns on the motor slowly, so get ready
  for (int commonMotorSpeed = 840; commonMotorSpeed < 1190; commonMotorSpeed++)
  {
    // motor starts up about half way through loop
    torqueSystem.writeSpeedToEsc(
        commonMotorSpeed, commonMotorSpeed, commonMotorSpeed, commonMotorSpeed);
    delay(20);
  }
} // speed will now jump to pot setting

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

  float euler[3];
  ahrs.eulerAngles(euler);

  controller.controlAction(attitudeError, angularVelocity, controls);

  float throttleFromRadio = radio.throttleReferencePercentage() * 1000 + 1000;
  float motor1 = throttleFromRadio + U_TO_PWM * (controls[0] + controls[1] + controls[2]);
  float motor2 = throttleFromRadio + U_TO_PWM * (-controls[0] + controls[1] - controls[2]);
  float motor3 = throttleFromRadio + U_TO_PWM * (controls[0] - controls[1] - controls[2]);
  float motor4 = throttleFromRadio + U_TO_PWM * (-controls[0] - controls[1] + controls[2]);
  torqueSystem.writeSpeedToEsc(motor1, motor2, motor3, motor4);

  // Serial.print(euler[1]);
  // Serial.print(", ");
  // Serial.print(controls[0]);
  // Serial.print(", ");
  // Serial.print(controls[1]);
  // Serial.print(", ");
  // Serial.println(controls[2]);

  // float throttlePrcntg = radio.throttleReferencePercentage();
  // int throttleToMotors = int (throttlePrcntg * 2000);
  // bzzz::logSerial(bzzz::LogVerbosityLevel::Severe, "throttlePrcntg = %f\n", throttlePrcntg);
  // torqueSystem.writeSpeedToEsc(throttleToMotors, throttleToMotors, throttleToMotors, throttleToMotors);
  // // delay(10);         // Wait for a while
}

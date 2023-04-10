#include <Arduino.h>
#include "controller.hpp"
#include "motors.hpp"
#include "imu.hpp"

void setup()
{
  Serial.begin(115200);
  bzzz::setupImu();
}

void loop()
{
  // quaternion
  float drone_quaternion[4] = {0};

  // check for new measurements from the IMU
  // note that the IMU runs at a certain frequency (250Hz),
  // but without using a timer
  if (bzzz::updateImu())
  {
    bzzz::quaternion(drone_quaternion);
    // compute control action
    float systemState = drone_quaternion[0];
    float voltage = bzzz::controlAction(systemState);
    // print control action
    Serial.println(voltage);
  }
}

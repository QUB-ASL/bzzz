#include <Arduino.h>
#include "controller.h"

void setup()
{
  Serial.begin(115200);
}

void loop()
{
  // compute control action
  float voltage = control_action(0.5);
  // print control action
  Serial.println(voltage);
}

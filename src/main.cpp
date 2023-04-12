#include <Arduino.h>

#include "motors.hpp"

// Note: the following speeds may need to be modified for your particular hardware.
#define MIN_SPEED 1040 // speed just slow enough to turn motor off
#define MAX_SPEED 1240 // speed where my motor drew 3.6 amps at 12v.

long int val; // variable to read the value from the analog pin

void setup()
{
  Serial.begin(9600);
  delay(1000);

  bzzz::arm();

  delay(5000); // Wait a while

  // the following loop turns on the motor slowly, so get ready
  for (int i = 0; i < 500; i++)
  {                                   // run speed from 840 to 1190
    bzzz::writeSpeedToEsc((MIN_SPEED - 200 + i), (MIN_SPEED - 200 + i), (MIN_SPEED - 200 + i), (MIN_SPEED - 200 + i));  // motor starts up about half way through loop
    delay(20);
  }
} // speed will now jump to pot setting

void loop()
{
  bzzz::writeSpeedToEsc(1150, 1150, 1150, 1150); // sets the ESC speed
  delay(10);         // Wait for a while
}
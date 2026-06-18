#include <Arduino.h>
#include "config.hpp"
#include "motors.hpp"

bzzz::MotorDriver motorDriver;

void setup()
{
  motorDriver.attachAndArm();     // attach ESC and arm motors
} 

// =========================================================================
// TEST SELECTION SWITCH
// Comment out this define line if you want to run the Sine-Wave Test loop instead!
// =========================================================================
#define RUN_STOP_START_TEST 

#define PERIOD 10000. // Period milliseconds


// =========================================================================
// FUNCTIONAL LOOP 1: STOP-START MOTOR TEST
// =========================================================================
// #ifdef RUN_STOP_START_TEST

void loop()
{
  #if UAV_TYPE == UAV_TYPE_QUADCOPTER
  // HARDWARE TEST: STOP START MOTORS (QUADCOPTER 4 MOTORS)
  motorDriver.writeSpeedToEsc(1350, 1350, 1350, 1350); 
  
  #elif UAV_TYPE == UAV_TYPE_HEXACOPTER
  // HARDWARE TEST: STOP START MOTORS (HEXACOPTER 6 MOTORS)
  motorDriver.writeSpeedToEsc(1350, 1350, 1350, 1350, 1350, 1350); 
  #endif

  delay(1000);                                         
  motorDriver.disarm();                                
  delay(1000); 
}

// =========================================================================
// FUNCTIONAL LOOP 2: PULSATING SINE-WAVE TEST
// =========================================================================
// #else

// void loop()
// {
//   for (float i = 0; i < PERIOD; i++)
//   {
//       // Calculate the pulsating speed variable
//       int commonMotorSpeed = ((ABSOLUTE_MAX_PWM - ZERO_ROTOR_SPEED) / 2) 
//                            * (sin(2. * PI * i * (1. / PERIOD)) + 1.) + ZERO_ROTOR_SPEED;
      
//       #if UAV_TYPE == UAV_TYPE_QUADCOPTER
//       // Pass the speed to ALL 4 quadcopter motors
//       motorDriver.writeSpeedToEsc(commonMotorSpeed, commonMotorSpeed, 
//                                   commonMotorSpeed, commonMotorSpeed);
      
//       #elif UAV_TYPE == UAV_TYPE_HEXACOPTER
//       // Pass the speed to ALL 6 hexacopter motors
//       motorDriver.writeSpeedToEsc(commonMotorSpeed, commonMotorSpeed, 
//                                   commonMotorSpeed, commonMotorSpeed, 
//                                   commonMotorSpeed, commonMotorSpeed);
//       #endif
      
//       delay(1); // Wait 1 millisecond before updating the speed
//   }
// }

// #endif
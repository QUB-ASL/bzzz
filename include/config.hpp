#include <Arduino.h>

#ifndef GLOBALS_H
#define GLOBALS_H

/*
 * IMU config
 */
#define IMU_ADDRESS (0x68)

/*
 * Motors config
 */
#define FRONT_LEFT_ESC_PIN 2
#define FRONT_RIGHT_ESC_PIN 3
#define BACK_LEFT_ESC_PIN 4
#define BACK_RIGHT_ESC_PIN 5

#define ARM_ROTOR_SPEED 900
#define ZERO_ROTOR_SPEED 1000
#define IDLE_ROTOR_SPEED 1130
#define ABSOLUTE_MIN_PWM 800
#define ABSOLUTE_MAX_PWM 2000

#define U_TO_PWM 10

#endif
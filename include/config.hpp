#include <Arduino.h>

#ifndef GLOBALS_H
#define GLOBALS_H

// Various defines such as PIN numbers and global constants

/**
 * IMU config
 */
#define IMU_ADDRESS (0x68)

/**
 * Serial config
 */
#define SERIAL_BAUD_RATE 500000

/** Sampling time */
#define SAMPLING_TIME (0.008)

/*
 * AHRS config
 */
#define MAGNETOMETER_BIAS_X 61.733
#define MAGNETOMETER_BIAS_Y -34.498
#define MAGNETOMETER_BIAS_Z -611.183

#define MAGNETOMETER_SCALE_X 1.083
#define MAGNETOMETER_SCALE_Y 1.108
#define MAGNETOMETER_SCALE_Z 0.852

/*
 * Motors config
 */
#define FRONT_LEFT_ESC_PIN 33
#define FRONT_RIGHT_ESC_PIN 32
#define BACK_LEFT_ESC_PIN 26
#define BACK_RIGHT_ESC_PIN 25

#define ARM_ROTOR_SPEED 900
#define ZERO_ROTOR_SPEED 1000
#define IDLE_ROTOR_SPEED 1130
#define ABSOLUTE_MIN_PWM 800
#define ABSOLUTE_MAX_PWM 2000

/**
 * Buzzer pin
 */
#define BUZZER_PIN 27

/** Maximum pitch value corresponding to the top position of the stick (30deg = 0.52rad) */
#define PITCH_MAX_RAD 0.5235987755982988

/** Value from the radio when the stick is at the lowest position */
#define RADIO_STICK_MIN 300

/** Value from the radio when the stick is at the highest position */
#define RADIO_STICK_MAX 1700

/** Maximum yaw rate (rad/s) 10 deg/s = 0.1745 rad/s */
#define RADIO_MAX_YAW_RATE_RAD_SEC 0.1745

/** Trimmer A on RC - maximum quaternion XY gain */
#define RADIO_TRIMMER_MAX_QUATERNION_XY_GAIN 100.

/** Trimmer B on RC - maximum quaternion Z gain */
#define RADIO_TRIMMER_MAX_QUATERNION_Z_GAIN 100.

/** Trimmer C on RC - maximum omega xy gain */
#define RADIO_TRIMMER_MAX_OMEGA_XY_GAIN 0.5

/** Trimmer E on RC - maximum omega z gain */
#define RADIO_TRIMMER_MAX_OMEGA_Z_GAIN 10

/**
 * Control action to PWM scaling factor
 */
#define U_TO_PWM 8

#ifndef BZZZ_LOGGING_LEVEL
#define BZZZ_LOGGING_LEVEL 3
#endif

#endif /* GLOBALS_H */
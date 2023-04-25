#include <Arduino.h>

#ifndef GLOBALS_H
#define GLOBALS_H

// Various defines such as PIN numbers and global constants

/*
 * IMU config
 */
#define IMU_ADDRESS (0x68)

/*
 * Serial config
 */
#define SERIAL_BAUD_RATE 115200

/** Sampling time */
#define SAMPLING_TIME (0.008)

/*
*AHRS config
*/
#define MAGNETOMETER_BIAS_X 222.566
#define MAGNETOMETER_BIAS_Y 41.087
#define MAGNETOMETER_BIAS_Z -60.268

#define MAGNETOMETER_SCALE_X 1.050
#define MAGNETOMETER_SCALE_Y 0.936
#define MAGNETOMETER_SCALE_Z 1.022

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
#define ABSOLUTE_MIN_PWM 1000
#define ABSOLUTE_MAX_PWM 2000

/* Maximum pitch value corresponding to the top position of the stick (30deg = 0.52rad) */
#define PITCH_MAX_RAD 0.5235987755982988

/* Value from the radio when the stick is at the lowest position */
#define RADIO_STICK_MIN 300

/* Value from the radio when the stick is at the highest position */
#define RADIO_STICK_MAX 1700

/* Maximum yaw rate (rad/s) 10 deg/s = 0.1745 rad/s */
#define RADIO_MAX_YAW_RATE_RAD_SEC 0.1745

#define U_TO_PWM 8

#ifndef BZZZ_VERBOSITY
#define BZZZ_VERBOSITY 3
#endif

// Various global utilities

namespace bzzz
{

    /**
     * Possible verbosity levels
     */
    enum LogVerbosityLevel
    {
        Debug = 1,
        Info = 2,
        Severe = 3
    };

    /**
     * @brief print debug information to the serial
     *
     * @param fmt string format
     *
     * @param ...
     */
    void logSerial(LogVerbosityLevel verbosity,
                   const char *fmt, ...);

}

#endif /* GLOBALS_H */
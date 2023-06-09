#include "config.hpp"

#ifndef BZZZ_UTILS_H
#define BZZZ_UTILS_H

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

    /**
     * Setup the buzzer
     */
    void setupBuzzer();

    /**
     * Make bzzz's buzzer beep
     *
     * This will produce `numBeeps` beeps of duration
     * `durationMs` (in milliseconds) with equal pauses
     * between the beeps.
     *
     * @param numBeeps number of beeps
     * @param durationMs duration of every beep in ms
     */
    void buzz(int numBeeps = 4, int durationMs = 50);

    /**
     * Wait until Raspberry Pi sends some data
     */
    void waitForPiSerial();

    /**
     * Maps a percentage to a value in an interval
     *
     * It returns minVal + percentage * (maxVal - minVal)
     *
     * @param percentage percentage; a value in [0, 1]
     * @param minVal minimum value
     * @param maxVal maximum value
     *
     * @return value between minVal and maxVal
     */
    float mapPrcnt(float percentage, float minVal, float maxVal);

}

#endif /* BZZZ_UTILS_H */
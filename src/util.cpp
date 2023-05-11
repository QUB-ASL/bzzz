#include "util.hpp"
#include <stdarg.h>

namespace bzzz
{

    void logSerial(LogVerbosityLevel verbosity,
                   const char *fmt, ...)
    {
        if (verbosity >= BZZZ_LOGGING_LEVEL)
        {
            char buf[64] = {0};
            va_list va;
            va_start(va, fmt);
            vsprintf(buf, fmt, va);
            Serial.println(buf);
            va_end(va);
        }
    }

    void setupBuzzer()
    {
        pinMode(BUZZER_PIN, OUTPUT);
        digitalWrite(BUZZER_PIN, LOW); // turn off the buzzer
    }

    void buzz(int numBeeps, int durationMs)
    {
        for (int i = 0; i < numBeeps; i++)
        {
            digitalWrite(BUZZER_PIN, HIGH);
            delay(durationMs);
            digitalWrite(BUZZER_PIN, LOW);
            delay(durationMs);
        }
    }

    void waitForPiSerial()
    {
        while (!Serial.available())
        {
            // just wait
        }
    }

    float mapPrcnt(float percentage, float minVal, float maxVal)
    {
        return minVal + percentage * (maxVal - minVal);
    }

}
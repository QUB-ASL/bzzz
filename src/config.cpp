
#include "config.hpp"
#include <stdarg.h>

namespace bzzz
{

    void logSerial(LogVerbosityLevel verbosity,
                   const char *fmt, ...)
    {
        if (verbosity >= BZZZ_VERBOSITY)
        {
            char buf[64] = {0};
            va_list va;
            va_start(va, fmt);
            vsprintf(buf, fmt, va);
            Serial.println(buf);
            va_end(va);
        }
    }

}
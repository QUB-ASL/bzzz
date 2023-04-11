
#include "config.hpp"
#include <stdarg.h>

namespace bzzz
{

    LogVerbosityLevel logLevel()
    {
#ifdef BZZZ_VERBOSITY

#if BZZZ_VERBOSITY == 1
        return LogVerbosityLevel::Debug;
#elif BZZZ_VERBOSITY == 2
        return LogVerbosityLevel::Info;
#endif

#endif
        return LogVerbosityLevel::Severe;
    }

    void logSerial(LogVerbosityLevel verbosity,
                   const char *fmt, ...)
    {
        if (verbosity >= bzzz::logLevel())
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
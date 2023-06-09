#include "fail_safes.hpp"
#include "util.hpp"

namespace bzzz
{
    FailSafes::FailSafes(unsigned long timeout)
    {
        m_radioConnectionTimeoutInMicroseconds = timeout;
    }

    void FailSafes::setLastRadioReceptionTime(long long lastRadioReceptionTime)
    {
        // Set private variable
        m_lastRadioReceptionTime = lastRadioReceptionTime;
    }

    bool FailSafes::isSerialTimeout()
    {
        unsigned long elapsedTime = micros() - m_lastRadioReceptionTime;
        return elapsedTime > m_radioConnectionTimeoutInMicroseconds;
    }

}
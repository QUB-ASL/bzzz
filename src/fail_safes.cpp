#include "fail_safes.hpp"
#include "util.hpp"

namespace bzzz
{
    FailSafes::FailSafes(){};

    void FailSafes::setLastRadioReceptionTime(long long lastRadioReceptionTime)
    {
        // Set private variable
        m_lastRadioReceptionTime = lastRadioReceptionTime;
    }

    void FailSafes::setRadioConnectionTimeoutInMicroseconds(unsigned long timeout)
    {
        // Set private variable
        m_radioConnectionTimeoutInMicroseconds = timeout;
    }

    bool FailSafes::radioConnectionCheck()
    {
        // Check radio connection and timeout if connection had been lost for a preset amount of time.
        if (micros() - m_lastRadioReceptionTime > m_radioConnectionTimeoutInMicroseconds)
        {
            m_HALT_SYSTEM = true;
            return false;
        }
        m_HALT_SYSTEM = false;
        return true;
    }

    bool FailSafes::isSerialTimeout()
    {
        return m_HALT_SYSTEM;
    }

}
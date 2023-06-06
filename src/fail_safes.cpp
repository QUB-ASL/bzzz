#include "fail_safes.hpp"
#include "util.hpp"

namespace bzzz
{
    FailSafes::FailSafes(){};

    FailSafes::FailSafes(MotorDriver &motorDriver)
    {
        m_motorDriver = motorDriver;
    }

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

    void FailSafes::shutDown()
    {
        // Currently only stalls the motors
        m_motorDriver.disarm();
        logSerial(LogVerbosityLevel::Severe, "[FAIL SAFE] Tx connection lost...\nSystem halted!");
    }

    bool FailSafes::haltSystem()
    {
        return m_HALT_SYSTEM;
    }

    void FailSafes::runFailSafes()
    {
        if (!radioConnectionCheck())
            shutDown();
    }
}
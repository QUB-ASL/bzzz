#include "fail_safes.hpp"
#include "util.hpp"


namespace bzzz
{
    FailSafes::FailSafes(){};

    void FailSafes::setLastRadioReceptionTime(long long lastRadioReceptionTime)
    {
        // Set private variable
        this->m_lastRadioReceptionTime = lastRadioReceptionTime;
    }

    void FailSafes::setRadioConnectionTimeoutInMicroseconds(unsigned long timeout)
    {
        //Set private variable
        this->m_radioConnectionTimeoutInMicroseconds = timeout;
    }

    bool FailSafes::radioConnectionCheck()
    {
        // Check radio connection and timeout if connection had been lost for a preset amount of time.
        if(micros() - this->m_lastRadioReceptionTime > this->m_radioConnectionTimeoutInMicroseconds)
        {
            this->m_HALT_SYSTEM = true;
            return false;
        }
        this->m_HALT_SYSTEM = false;
        return true;
    }

    void FailSafes::setMotorDriverObjPtr(MotorDriver *motorDriverObj)
    {
        this->motorDriver = motorDriverObj;
    }

    void FailSafes::shutDown()
    {
        // Currently only stalls the motors
        this->motorDriver->disarm();
        logSerial(LogVerbosityLevel::Severe, "[FAIL SAFE] Tx connection lost...\nSystem halted!");
    }
    
    bool FailSafes::haltSystem(){
        return this->m_HALT_SYSTEM;
    }

    void FailSafes::runFailSafes()
    {
        if(!radioConnectionCheck()) shutDown();
    }
}
#include "fail_safes.hpp"


namespace bzzz
{
    FailSafes::FailSafes(){};

    void FailSafes::setLastRadioReceptionTime(long long t)
    {
        // Set private variable
        m_lastRadioReceptionTime = t;
    }

    void FailSafes::setRadioConnectionTimeoutInMicroseconds(long timeout)
    {
        //Set private variable
        m_radioConnectionTimeoutInMicroseconds = timeout;
    }

    bool FailSafes::radioConnectionCheck()
    {
        // Check radio connection and timeout if connection had been lost for a preset amount of time.
        if(micros() - m_lastRadioReceptionTime > m_radioConnectionTimeoutInMicroseconds)return false;
        else return true;
    }

    void FailSafes::setMotorDriverObjPtr(MotorDriver *motorDriverObj)
    {
        motorDriver = motorDriverObj;
    }

    void FailSafes::shutDown()
    {
        // Currently only stalls the motors
        motorDriver->disarm();
    }

    void FailSafes::runFailSafes()
    {
        if(!radioConnectionCheck()) shutDown();
    }
}
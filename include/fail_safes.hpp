#include "config.hpp"
#include "motors.hpp"

namespace bzzz
{
    class FailSafes
    {
        private:
        /**
         * Radio timeout variables for connection loss check
        */
       unsigned long long m_lastRadioReceptionTime;
       unsigned long m_radioConnectionTimeoutInMicroseconds;
       bool m_HALT_SYSTEM = false;  // Bool to keep keep track if any fail-safe triggers a system halt.

       /**
        * Poiters to useful objects that are declared outside of this scope
        * 
        * Current list of objects pointer:
        * 1. of class MotorDriver -> this is declared in main.cpp,
        *                           used to control motors.
       */
       MotorDriver *motorDriver;

       /**
        * Check the radio connection and return true if it timed out 
        * as follows:
        * 
        * if (micros - lastRadioreceptionTime > timeout) then the connection has been lost 
        * and return false; otherwise return true
        * 
        * The function uses the system start time as reference and micros is the time since the 
        * system was up.
       */
       bool radioConnectionCheck();

       /**
        * Shutdown the entire system
        * 
        * Currently only stalls the motors,
        * might need to include a proper shutdown procedure in the future
       */
       void shutDown();

       public:
       /**
        * Default constructor
       */
       FailSafes();

       /**
        * Set timeout time for radio connection in micro-seconds
        * 
        * When the connection is lost, the system will wait for the
        * provided number of micro-seconds before declaring that the 
        * connection had been lost
        * 
        * @param timeout number of micro-seconds to wait till timeout
        *                Default: 500000 micro-seconds or 500 milli-seconds
       */
       void setRadioConnectionTimeoutInMicroseconds(unsigned long timeout = 500000);

       /**
        * Set the last time in micro-seconds at which radio data was heard
        * 
        * This is used to keep track of when the connection might have been lost,
        * based on which the timeout mechanism triggers.
        * 
        * @param t last time in micro-seconds at which the radio was heard
       */
       void setLastRadioReceptionTime(long long t);

       /**
        * set the stopMotor function pointer to point to the actual function implementation 
        * which stalls the motors
       */
      void setMotorDriverObjPtr(MotorDriver *motorDriverObj);

      
       /**
        * @return HALT_SYSTEM bool status
       */
      bool haltSystem();

       /**
        * Runs all of the implemented fail safe checks one by one and takes appropriate action
        * based on received triggers.
        * 
        * Current implement mechanisms and associated actions:
        * 1. Check radio connection, if lost and timed out shutdown the system
       */
       void runFailSafes();

    };
}
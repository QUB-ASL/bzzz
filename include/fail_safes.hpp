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
        unsigned long m_lastRadioReceptionTime;
        /**
         * Timeout time
         */
        unsigned long m_radioConnectionTimeoutInMicroseconds;

    public:
        /**
         * Default constructor
         */
        FailSafes(unsigned long timeout = 500000);

        /**
         * Set the last time in micro-seconds at which radio data was heard
         *
         * This is used to keep track of when the connection might have been lost,
         * based on which the timeout mechanism triggers.
         *
         * @param t last time in micro-seconds at which the radio was heard
         */
        void setLastRadioReceptionTime(long long lastRadioReceptionTime);

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
        bool isSerialTimeout();
    };
}
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
        bool m_HALT_SYSTEM = false; // Bool to keep keep track if any fail-safe triggers a system halt.

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
        void setLastRadioReceptionTime(long long lastRadioReceptionTime);

        /**
         * @return HALT_SYSTEM bool status
         */
        bool isSerialTimeout();
    };
}

#include "motors.hpp"

namespace bzzz
{
    static bool s_armStatus = false;

    void attachMotors(void){
        // todo
    };

    void writeSpeedToEsc(void){
        // todo
    };

    void disarm(void)
    {
        bzzz::s_armStatus = 0;
        // todo
    };

    void arm(void)
    {
        bzzz::s_armStatus = 1;
        // todo
    };

    bool getArmStatus(void)
    {
        return bzzz::s_armStatus;
    };

}
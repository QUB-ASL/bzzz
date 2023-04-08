
#include "motors.hpp"

namespace bzzz
{
    static bool g_armStatus = false;

    void attachMotors(void){
        // todo
    };

    void writeSpeedToEsc(void){
        // todo
    };

    void disarm(void)
    {
        bzzz::g_armStatus = 0;
        // todo
    };

    void arm(void)
    {
        bzzz::g_armStatus = 1;
        // todo
    };

    bool getArmStatus(void)
    {
        return bzzz::g_armStatus;
    };

}
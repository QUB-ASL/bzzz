#include "controller.hpp"
#include <math.h>

namespace bzzz
{

    Controller::Controller(){};

    void Controller::controlAction(
        Quaternion &attitudeError,
        const float *angularVelocity,
        float *control)
    {

        for (int i = 0; i < 3; i++)
        {
            control[i] = m_quaternionGain[i] * attitudeError[i + 1] + m_angularVelocityGain[i] * angularVelocity[i];
        }
    }

#ifdef BZZZ_DEBUG
    void Controller::setQuaternionGains(float gainXY, float gainZ)
    {
        m_quaternionGain[0] = gainXY;
        m_quaternionGain[1] = gainXY;
        m_quaternionGain[2] = gainZ;
    }

    void Controller::setAngularVelocityGains(float gainXY, float gainZ)
    {
        m_angularVelocityGain[0] = gainXY;
        m_angularVelocityGain[1] = gainXY;
        m_angularVelocityGain[2] = gainZ;
    }
#endif /* BZZZ_DEBUG */

}
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

    void Controller::motorPwmSignals(
        Quaternion &attitudeError,
        const float *angularVelocity,
        float throttle,
        int &motorFL,
        int &motorFR,
        int &motorBL,
        int &motorBR,
        float controlToPwmScaling)
    {
        float controls[3];
        controlAction(attitudeError, angularVelocity, controls);
        motorFL = throttle + controlToPwmScaling * (controls[0] + controls[1] + controls[2]);
        motorFR = throttle + controlToPwmScaling * (-controls[0] + controls[1] - controls[2]);
        motorBL = throttle + controlToPwmScaling * (controls[0] - controls[1] - controls[2]);
        motorBR = throttle + controlToPwmScaling * (-controls[0] - controls[1] + controls[2]);
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

} /* end of namespace bzzz */
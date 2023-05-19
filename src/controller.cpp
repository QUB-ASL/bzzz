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

    template <typename _Tp>
    inline const _Tp &
    clip(const _Tp &x, const _Tp &lo, const _Tp &hi)
    {
        return max(lo, min(hi, x));
    }

    void Controller::motorPwmSignals(
        Quaternion &attitudeError,
        const float *angularVelocity,
        float throttle,
        int &motorFL,
        int &motorFR,
        int &motorBL,
        int &motorBR,
        float controlToPwmScaling,
        int motorClipLow,
        int motorClipHigh)
    {
        float controls[3];
        // compute control actions (LQR)
        controlAction(attitudeError, angularVelocity, controls);
        // compute motor signals from control actions (and cast float as int)
        int mFL = throttle + controlToPwmScaling * (controls[0] + controls[1] + controls[2]);
        int mFR = throttle + controlToPwmScaling * (-controls[0] + controls[1] - controls[2]);
        int mBL = throttle + controlToPwmScaling * (controls[0] - controls[1] - controls[2]);
        int mBR = throttle + controlToPwmScaling * (-controls[0] - controls[1] + controls[2]);
        // clip motor signals between motorClipLow and motorClipHigh
        motorFL = clip(mFL, motorClipLow, motorClipHigh);
        motorFR = clip(mFR, motorClipLow, motorClipHigh);
        motorBL = clip(mBL, motorClipLow, motorClipHigh);
        motorBR = clip(mBR, motorClipLow, motorClipHigh);
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
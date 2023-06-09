#include "controller.hpp"
#include <math.h>
#include "util.hpp"

namespace bzzz
{

    Controller::Controller(){};

    void Controller::controlAction(
        Quaternion &attitudeError,
        const float *angularVelocity,
        float angularVelocityYawRef,
        float *control)
    {

        for (int i = 0; i < 2; i++)
        {
            control[i] = m_quaternionGain[i] * attitudeError[i + 1];
        }
        control[0] += m_angularVelocityGain[0] * angularVelocity[0];
        control[1] += m_angularVelocityGain[1] * angularVelocity[1];
        float yawRateError = angularVelocity[2] - angularVelocityYawRef;

        control[2] = m_angularVelocityGain[2] * yawRateError;
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
        float angularVelocityYawRef,
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
        controlAction(attitudeError, angularVelocity, angularVelocityYawRef, controls);
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
    void Controller::setQuaternionGain(float gainXY)
    {
        m_quaternionGain[0] = gainXY;
        m_quaternionGain[1] = gainXY;
    }

    void Controller::setAngularVelocityXYGain(float gainOmegaXY)
    {
        m_angularVelocityGain[0] = gainOmegaXY;
        m_angularVelocityGain[1] = gainOmegaXY;
    }
    void Controller::setYawAngularVelocityGain(float gainOmegaZ)
    {
        m_angularVelocityGain[2] = gainOmegaZ;
    }
#endif /* BZZZ_DEBUG */

} /* end of namespace bzzz */
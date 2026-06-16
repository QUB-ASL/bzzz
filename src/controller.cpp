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
        /*
         * ux = Kqx * qx + Kwx * wx
         * uy = Kqy * qy + Kwy * wy
         * uz = Kwz * err_wz
         */
        control[0] = m_quaternionGain[0] * attitudeError[1];             // qx
        control[1] = m_quaternionGain[1] * attitudeError[2];             // qy
        control[0] += m_angularVelocityGain[0] * angularVelocity[0];     // wx
        control[1] += m_angularVelocityGain[1] * angularVelocity[1];     // wy
        float yawRateError = angularVelocity[2] - angularVelocityYawRef; //
        control[2] = m_angularVelocityGain[2] * yawRateError;            // u_z = Kz * err_wz
    }

    template <typename _Tp>
    inline const _Tp &
    clip(const _Tp &x, const _Tp &lo, const _Tp &hi)
    {
        return max(lo, min(hi, x));
    }

#if DRONE_TYPE == QUADCOPTER_TYPE

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

        controlAction(attitudeError,
                      angularVelocity,
                      angularVelocityYawRef,
                      controls);

        int mFL = throttle + controlToPwmScaling * (controls[0] + controls[1] + controls[2]);
        int mFR = throttle + controlToPwmScaling * (-controls[0] + controls[1] - controls[2]);
        int mBL = throttle + controlToPwmScaling * (controls[0] - controls[1] - controls[2]);
        int mBR = throttle + controlToPwmScaling * (-controls[0] - controls[1] + controls[2]);

        motorFL = clip(mFL, motorClipLow, motorClipHigh);
        motorFR = clip(mFR, motorClipLow, motorClipHigh);
        motorBL = clip(mBL, motorClipLow, motorClipHigh);
        motorBR = clip(mBR, motorClipLow, motorClipHigh);
    }

#elif DRONE_TYPE == HEXACOPTER_TYPE

    void Controller::motorPwmSignals(
        Quaternion &attitudeError,
        const float *angularVelocity,
        float angularVelocityYawRef,
        float throttle,
        int &motorFL,
        int &motorFR,
        int &motorML,
        int &motorMR,
        int &motorBL,
        int &motorBR,
        float controlToPwmScaling,
        int motorClipLow,
        int motorClipHigh)
    {
        float controls[3];

        controlAction(attitudeError,
                      angularVelocity,
                      angularVelocityYawRef,
                      controls);

        float ux = controls[0];
        float uy = controls[1];
        float uz = controls[2];

        int mFR = throttle + controlToPwmScaling *
            (0.5000f * ux - 0.1340f * uy + 0.1340f * uz);

        int mFL = throttle + controlToPwmScaling *
            (0.5000f * ux + 0.1340f * uy - 0.1340f * uz);

        int mML = throttle + controlToPwmScaling *
            (0.2679f * uy + 0.2321f * uz);

        int mBL = throttle + controlToPwmScaling *
            (-0.5000f * ux + 0.1340f * uy - 0.1340f * uz);

        int mBR = throttle + controlToPwmScaling *
            (-0.5000f * ux - 0.1340f * uy + 0.1340f * uz);

        int mMR = throttle + controlToPwmScaling *
            (-0.2679f * uy - 0.2321f * uz);

        motorFL = clip(mFL, motorClipLow, motorClipHigh);
        motorFR = clip(mFR, motorClipLow, motorClipHigh);
        motorML = clip(mML, motorClipLow, motorClipHigh);
        motorMR = clip(mMR, motorClipLow, motorClipHigh);
        motorBL = clip(mBL, motorClipLow, motorClipHigh);
        motorBR = clip(mBR, motorClipLow, motorClipHigh);
    }

#endif

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

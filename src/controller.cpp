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
//         Serial.printf(
//     "attErr=[%.3f %.3f %.3f %.3f] | wx=%.3f wy=%.3f\n",
//     attitudeError[0],
//     attitudeError[1],
//     attitudeError[2],
//     attitudeError[3],
//     angularVelocity[0],
//     angularVelocity[1]

 
// );
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

#if UAV_TYPE == UAV_TYPE_QUADCOPTER
    /**
     * Compute PWM signals for motors (quadcopter version).
     * Uses control outputs from controlAction() and maps them to 4 motors.
     */
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
        float controls[3] = {0.0f, 0.0f, 0.0f};
        // compute control actions (LQR)
        controlAction(attitudeError, angularVelocity, angularVelocityYawRef, controls);
        m_lastControl[0] = controls[0];   // roll
        m_lastControl[1] = controls[1];   // pitch
        m_lastControl[2] = controls[2];   // yaw
  

        // compute motor signals from control actions (and cast float as int)
        int mFL = throttle + controlToPwmScaling * ( controls[0] + controls[1] + controls[2]);
        int mFR = throttle + controlToPwmScaling * (-controls[0] + controls[1] - controls[2]);
        int mBL = throttle + controlToPwmScaling * ( controls[0] - controls[1] - controls[2]);
        int mBR = throttle + controlToPwmScaling * (-controls[0] - controls[1] + controls[2]);

        // clip motor signals between motorClipLow and motorClipHigh
        motorFL = clip(mFL, motorClipLow, motorClipHigh);
        motorFR = clip(mFR, motorClipLow, motorClipHigh);
        motorBL = clip(mBL, motorClipLow, motorClipHigh);
        motorBR = clip(mBR, motorClipLow, motorClipHigh);
    }
#elif UAV_TYPE == UAV_TYPE_HEXACOPTER

    

    /**
     * Compute PWM signals for motors (hexacopter version).
     * Uses control outputs from controlAction() and maps them to 6 motors.
     */
    void Controller::motorPwmSignals(
        Quaternion &attitudeError,
        const float *angularVelocity,
        float angularVelocityYawRef,
        float throttle,
        int &motorFL,
        int &motorFR,
        int &motorBL,
        int &motorBR,
        int &motorML,  // middle left
        int &motorMR,  // middle right
        float controlToPwmScaling,
        int motorClipLow,
        int motorClipHigh)
    {
        float controls[3] = {0.0f, 0.0f, 0.0f};
        // compute control actions (LQR)
        controlAction(attitudeError, angularVelocity, angularVelocityYawRef, controls);

        m_lastControl[0] = controls[0];   // roll
        m_lastControl[1] = controls[1];   // pitch
        m_lastControl[2] = controls[2];   // yaw

        int mFR = throttle + controlToPwmScaling * ( 0.5f * controls[1] - 0.134f * controls[0] - 0.134f * controls[2]);
        int mFL = throttle + controlToPwmScaling * ( 0.5f * controls[1] + 0.134f * controls[0] + 0.134f * controls[2]);
        int mBL = throttle + controlToPwmScaling * (-0.5f * controls[1] + 0.134f * controls[0] + 0.134f * controls[2]);
        int mBR = throttle + controlToPwmScaling * (-0.5f * controls[1] - 0.134f * controls[0] - 0.134f * controls[2]);
        int mML = throttle + controlToPwmScaling * (                     0.2679f * controls[0] - 0.2321f * controls[2]);
        int mMR = throttle + controlToPwmScaling * (                    -0.2679f * controls[0] + 0.2321f * controls[2]);





        // clip motor signals between motorClipLow and motorClipHigh
        motorFR = clip(mFR, motorClipLow, motorClipHigh);
        motorFL = clip(mFL, motorClipLow, motorClipHigh);
        motorML = clip(mML, motorClipLow, motorClipHigh);
        motorBL = clip(mBL, motorClipLow, motorClipHigh);
        motorBR = clip(mBR, motorClipLow, motorClipHigh);
        motorMR = clip(mMR, motorClipLow, motorClipHigh);
    }


#endif

 void Controller::getLastControl(float *control) const
        {
            control[0] = m_lastControl[0];
            control[1] = m_lastControl[1];
            control[2] = m_lastControl[2];
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

} /* end of namespace bzzz *//* end of namespace bzzz */

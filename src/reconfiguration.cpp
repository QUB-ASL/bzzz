#include "reconfiguration.hpp"
#include <math.h>
#include "util.hpp"

namespace bzzz
{

    Reconfiguration::Reconfiguration(){};


    void Reconfiguration::controlAction(
        Quaternion &attitudeError,
        const float *angularVelocity,
        float angularVelocityYawRef,
        float *control)
    {
        /*
         * Same controller law as Controller:
         *
         * ux = Kqx * qx + Kwx * wx
         * uy = Kqy * qy + Kwy * wy
         * uz = Kwz * err_wz
         *
         * control[0] = roll
         * control[1] = pitch
         * control[2] = yaw
         */

        control[0] = m_quaternionGain[0] * attitudeError[1];          // qx
        control[1] = m_quaternionGain[1] * attitudeError[2];          // qy

        control[0] += m_angularVelocityGain[0] * angularVelocity[0];  // wx
        control[1] += m_angularVelocityGain[1] * angularVelocity[1];  // wy

        float yawRateError = angularVelocity[2] - angularVelocityYawRef;

        control[2] = m_angularVelocityGain[2] * yawRateError;         // uz
    }


    template <typename _Tp>
    inline const _Tp &
    clip(const _Tp &x, const _Tp &lo, const _Tp &hi)
    {
        return max(lo, min(hi, x));
    }


#if UAV_TYPE == UAV_TYPE_HEXACOPTER

    /**
     * Compute PWM signals according to the locked fault
     * hypothesis.
     *
     * hypothesis:
     *
     *     H1 = FL failed
     *     H2 = FR failed
     *     H3 = MR failed
     *     H4 = BR failed
     *     H5 = BL failed
     *     H6 = ML failed
     *
     * MATLAB M+ column order:
     *
     *     [PITCH, ROLL, YAW, THRUST]
     *
     * C++ control order:
     *
     *     controls[0] = ROLL
     *     controls[1] = PITCH
     *     controls[2] = YAW
     *
     * The existing C++ throttle is used as the
     * common PWM thrust baseline.
     */
    void Reconfiguration::motorPwmSignals(
        int hypothesis,
        Quaternion &attitudeError,
        const float *angularVelocity,
        float angularVelocityYawRef,
        float throttle,
        int &motorFL,
        int &motorFR,
        int &motorBL,
        int &motorBR,
        int &motorML,
        int &motorMR,
        float controlToPwmScaling,
        int motorClipLow,
        int motorClipHigh)
    {
        float controls[3] = {0.0f, 0.0f, 0.0f};

        /*
         * Compute control actions using the same
         * quaternion/angular-velocity controller law
         * as the nominal Controller.
         */
        controlAction(
            attitudeError,
            angularVelocity,
            angularVelocityYawRef,
            controls);


        /*
         * Motor PWM values before clipping.
         *
         * They are initialized to the throttle baseline so
         * every motor has a defined value even before the
         * fault-specific allocation is applied.
         */
        int mFL = throttle;
        int mFR = throttle;
        int mBL = throttle;
        int mBR = throttle;
        int mML = throttle;
        int mMR = throttle;


        /*
         * =====================================================
         * FAULT RECONFIGURATION
         * =====================================================
         *
         * The selected allocation depends on the locked
         * fault hypothesis.
         */
        switch (hypothesis)
        {

            
            // =================================================
            // H1: FL FAILED
            // =================================================
              case 1:
            {
                // H1: FL failed
                //
                // MATLAB:
                // FR =  0.7500 PITCH -0.0670 ROLL +0.0670 YAW +0.2500 THRUST
                // MR =  0.2500 PITCH +0.3349 ROLL +0.1651 YAW +0.2500 THRUST
                // BL = -0.2500 PITCH +0.2010 ROLL -0.2010 YAW +0.2500 THRUST
                // BR = -1.0000 PITCH -0.2679 ROLL +0.2679 YAW +0.0000 THRUST
                // ML =  0.2500 PITCH -0.2010 ROLL -0.2990 YAW +0.2500 THRUST
                //
                // H1 thrust allocation:
                // nominal = 1/6 per motor
                // failed  = 0
                // healthy = 1/4 per surviving motor
                //
                // 0.25 / 0.1667 ~= 1.5
                //
                // Convert the existing per-motor PWM throttle to
                // the equivalent H1 surviving-motor collective level.

                const float h1Throttle =
                    motorClipLow + 1.5f * (throttle - motorClipLow);

                // FL failed
                mFL = ZERO_ROTOR_SPEED;

                // FR
                mFR = h1Throttle + controlToPwmScaling * (
                    -0.0670f * controls[0]
                    +  0.7500f * controls[1]
                    +  0.0670f * controls[2]);

                // ML
                mML = h1Throttle + controlToPwmScaling * (
                    0.3349f * controls[0]
                    + 0.2500f * controls[1]
                    + 0.1651f * controls[2]);

                // BL
                mBL = h1Throttle + controlToPwmScaling * (
                    0.2010f * controls[0]
                    - 0.2500f * controls[1]
                    - 0.2010f * controls[2]);
                // BR
                mBR = controlToPwmScaling * (
                        -0.2679f * controls[0]
                        -1.0000f * controls[1]
                        +0.2679f * controls[2]);

                // MR
                mMR = h1Throttle + controlToPwmScaling * (
                    -0.2010f * controls[0]
                    +  0.2500f * controls[1]
                    -  0.2990f * controls[2]);

                // MR is already assigned above

                break;
            }


            // =================================================
            // H2: FR FAILED
            // =================================================
            case 2:
            {

                const float h2Throttle =
                    motorClipLow + 1.5f * (throttle - motorClipLow);
                /*
                 * Failed motor:
                 *     FR
                 *
                 * Surviving motors:
                 *     FL, ML, BL, BR, MR
                 */

                mFR = ZERO_ROTOR_SPEED;

                mFL = h2Throttle + controlToPwmScaling * (
                      0.0670f * controls[0]
                     +0.7500f * controls[1]
                     -0.0670f * controls[2]);

                mML = h2Throttle + controlToPwmScaling * (
                      0.2010f * controls[0]
                     +0.2500f * controls[1]
                     +0.2990f * controls[2]);

                mBL = controlToPwmScaling * (
                      0.2679f * controls[0]
                     -1.0000f * controls[1]
                     -0.2679f * controls[2]);

                mBR = h2Throttle + controlToPwmScaling * (
                     -0.2010f * controls[0]
                     -0.2500f * controls[1]
                     +0.2010f * controls[2]);

                mMR = h2Throttle + controlToPwmScaling * (
                     -0.3349f * controls[0]
                     +0.2500f * controls[1]
                     -0.1651f * controls[2]);

                break;
            }


            // =================================================
            // H3: MR FAILED
            // =================================================
            case 3:
            {
                const float h3Throttle =
                    motorClipLow + 1.5f * (throttle - motorClipLow);
                /*
                 * Failed motor:
                 *     MR
                 *
                 * Surviving motors:
                 *     FR, FL, ML, BL, BR
                 */

                mMR = ZERO_ROTOR_SPEED;

                mFR = h3Throttle + controlToPwmScaling * (
                     -0.2679f * controls[0]
                     +0.5000f * controls[1]
                     +0.0179f * controls[2]);

                mFL = h3Throttle + controlToPwmScaling * (
                      0.0000f * controls[0]
                     +0.5000f * controls[1]
                     -0.2500f * controls[2]);

                mML = controlToPwmScaling * (
                      0.5359f * controls[0]
                     +0.0000f * controls[1]
                     +0.4641f * controls[2]);

                mBL = h3Throttle + controlToPwmScaling * (
                      0.0000f * controls[0]
                     -0.5000f * controls[1]
                     -0.2500f * controls[2]);

                mBR = h3Throttle + controlToPwmScaling * (
                     -0.2679f * controls[0]
                     -0.5000f * controls[1]
                     +0.0179f * controls[2]);

                break;
            }


            // =================================================
            // H4: BR FAILED
            // =================================================
            case 4:
            {
                const float h4Throttle =
                    motorClipLow + 1.5f * (throttle - motorClipLow);
                /*
                 * Failed motor:
                 *     BR
                 *
                 * Surviving motors:
                 *     FR, FL, ML, BL, MR
                 */

                mBR = ZERO_ROTOR_SPEED;

                mFR = h4Throttle + controlToPwmScaling * (
                     -0.2010f * controls[0]
                     +0.2500f * controls[1]
                     +0.2010f * controls[2]);

                mFL = controlToPwmScaling * (
                      0.2679f * controls[0]
                     +1.0000f * controls[1]
                     -0.2679f * controls[2]);

                mML = h4Throttle + controlToPwmScaling * (
                      0.2010f * controls[0]
                     -0.2500f * controls[1]
                     +0.2990f * controls[2]);

                mBL = h4Throttle + controlToPwmScaling * (
                      0.0670f * controls[0]
                     -0.7500f * controls[1]
                     -0.0670f * controls[2]);

                mMR = h4Throttle + controlToPwmScaling * (
                     -0.3349f * controls[0]
                     -0.2500f * controls[1]
                     -0.1651f * controls[2]);

                break;
            }


            // =================================================
            // H5: BL FAILED
            // =================================================
            case 5:
{

    const float h5Throttle =
                    motorClipLow + 1.5f * (throttle - motorClipLow);
    // =================================================
    // H5: BL FAILED
    // =================================================
    //
    // MATLAB reduced allocation:
    //
    // FR = 0*T + (-0.2679)R + (1.0000)P + (0.2679)Y
    // FL = 0.25T + (0.2010)R + (0.2500)P + (-0.2010)Y
    // ML = 0.25T + (-0.2010)R + (-0.2500)P + (-0.2990)Y
    // BL = FAILED
    // BR = 0.25T + (-0.0670)R + (-0.7500)P + (0.0670)Y
    // MR = 0.25T + (0.3349)R + (-0.2500)P + (0.1651)Y
    //
    // C++:
    // controls[0] = ROLL
    // controls[1] = PITCH
    // controls[2] = YAW

    mBL = ZERO_ROTOR_SPEED;

    // FR: CONTROL ONLY
    mFR = controlToPwmScaling * (
        -0.2679f * controls[0]
        +1.0000f * controls[1]
        +0.2679f * controls[2]);

    // FL: THRUST + CONTROL
    mFL = h5Throttle + controlToPwmScaling * (
         0.2010f * controls[0]
        +0.2500f * controls[1]
        -0.2010f * controls[2]);

    // ML: THRUST + CONTROL
    mMR = h5Throttle + controlToPwmScaling * (
        -0.2010f * controls[0]
        -0.2500f * controls[1]
        -0.2990f * controls[2]);

    // BR: THRUST + CONTROL
    mBR = h5Throttle + controlToPwmScaling * (
        -0.0670f * controls[0]
        -0.7500f * controls[1]
        +0.0670f * controls[2]);

    // MR: THRUST + CONTROL
    mML = h5Throttle + controlToPwmScaling * (
         0.3349f * controls[0]
        -0.2500f * controls[1]
        +0.1651f * controls[2]);

    break;
}


            // =================================================
            // H6: ML FAILED
            // =================================================
            case 6:
            {

                 const float h6Throttle =
                    motorClipLow + 1.5f * (throttle - motorClipLow);
                /*
                 * Failed motor:
                 *     ML
                 *
                 * Surviving motors:
                 *     FR, FL, BL, BR, MR
                 */

                mML = ZERO_ROTOR_SPEED;

                mFR = h6Throttle + controlToPwmScaling * (
                      0.0000f * controls[0]
                     +0.5000f * controls[1]
                     +0.2500f * controls[2]);

                mFL = h6Throttle + controlToPwmScaling * (
                      0.2679f * controls[0]
                     +0.5000f * controls[1]
                     -0.0179f * controls[2]);

                mBL = h6Throttle + controlToPwmScaling * (
                      0.2679f * controls[0]
                     -0.5000f * controls[1]
                     -0.0179f * controls[2]);

                mBR = h6Throttle + controlToPwmScaling * (
                      0.0000f * controls[0]
                     -0.5000f * controls[1]
                     +0.2500f * controls[2]);

                mMR =  controlToPwmScaling * (
                     -0.5359f * controls[0]
                     +0.0000f * controls[1]
                     -0.4641f * controls[2]);

                break;
            }


            // =================================================
            // Invalid hypothesis
            // =================================================
            default:
            {
                /*
                 * H0 is handled by Controller in main.cpp.
                 *
                 * If an invalid hypothesis reaches this
                 * function, all motors are held at the
                 * minimum configured rotor speed.
                 */

                mFL = motorClipLow;
                mFR = motorClipLow;
                mBL = motorClipLow;
                mBR = motorClipLow;
                mML = motorClipLow;
                mMR = motorClipLow;

                break;
            }
        }


        /*
         * =====================================================
         * PWM LIMITING
         * =====================================================
         *
         * Apply the same clipping convention used by the
         * existing Controller.
         */
        motorFL = clip(mFL, motorClipLow, motorClipHigh);
        motorFR = clip(mFR, motorClipLow, motorClipHigh);
        motorML = clip(mML, motorClipLow, motorClipHigh);
        motorBL = clip(mBL, motorClipLow, motorClipHigh);
        motorBR = clip(mBR, motorClipLow, motorClipHigh);
        motorMR = clip(mMR, motorClipLow, motorClipHigh);
    }


#endif


#ifdef BZZZ_DEBUG

    void Reconfiguration::setQuaternionGain(float gainXY)
    {
        m_quaternionGain[0] = gainXY;
        m_quaternionGain[1] = gainXY;
    }


    void Reconfiguration::setAngularVelocityXYGain(float gainOmegaXY)
    {
        m_angularVelocityGain[0] = gainOmegaXY;
        m_angularVelocityGain[1] = gainOmegaXY;
    }


    void Reconfiguration::setYawAngularVelocityGain(float gainOmegaZ)
    {
        m_angularVelocityGain[2] = gainOmegaZ;
    }

#endif /* BZZZ_DEBUG */

} /* namespace bzzz */

#include "config.hpp"
#include "quaternion.hpp"

#ifndef RECONFIGURATION_H
#define RECONFIGURATION_H

namespace bzzz
{
    class Reconfiguration
    {
    private:

        float m_quaternionGain[3] = {-17., -17., -0.98};
        float m_angularVelocityGain[3] = {-1.4, -1.55, -1.08};

        /**
         * @brief Computes the control action using the
         *        same quaternion controller law as Controller.
         *
         * control[0] = roll
         * control[1] = pitch
         * control[2] = yaw
         */
        void controlAction(
            Quaternion &attitudeError,
            const float *angularVelocity,
            float angularVelocityYawRef,
            float *control);

    public:

        /**
         * @brief Constructs a new instance of Reconfiguration.
         */
        Reconfiguration();

        /**
         * @brief Generates PWM signals according to the
         *        locked fault hypothesis.
         *
         * hypothesis:
         *     1 = FL failed
         *     2 = FR failed
         *     3 = MR failed
         *     4 = BR failed
         *     5 = BL failed
         *     6 = ML failed
         *
         * The failed motor is forced to ZERO_ROTOR_SPEED.
         * The remaining five motors are reconfigured using
         * the corresponding control allocation matrix.
         */
        void motorPwmSignals(
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
            float controlToPwmScaling = U_TO_PWM,
            int motorClipLow = ZERO_ROTOR_SPEED,
            int motorClipHigh = ABSOLUTE_MAX_PWM);

#ifdef BZZZ_DEBUG

        void setQuaternionGain(float gainXY);

        void setAngularVelocityXYGain(float gainOmegaXY);

        void setYawAngularVelocityGain(float gainOmegaZ);

#endif /* BZZZ_DEBUG */
    };

} /* namespace bzzz */

#endif /* RECONFIGURATION_H */
#include "config.hpp"
#include "quaternion.hpp"

#ifndef CONTROLLER_H
#define CONTROLLER_H

// I have the impression that "#pragma once" is not
// supported on ESP32

namespace bzzz
{

    class Controller
    {
    private:
        /**
         * Gain values for the quaternion
         */
        float m_quaternionGain[3] = {-17., -17., -0.98};

        /**
         * Gain values for the angular velocity
         */
        float m_angularVelocityGain[3] = {-1.4, -1.55, -1.08};

    public:
        /**
         * Constructs a new instance of Controller
         */
        Controller();

/*
The following functions should only be defined/used when in debug mode.
The idea is to allow to fine-tune the gain values using the trimmers on
the RC.
*/
#ifdef BZZZ_DEBUG
        /**
         * Set the gains of the quaternion
         */
        void setQuaternionGains(float gainXY, float gainZ);

        /**
         * Set the gains of the angular velocity
         */
        void setAngularVelocityGains(float gainXY, float gainZ);
#endif /* BZZZ_DEBUG */

        /**
         * @brief computes control action
         *
         * @param attitudeError attitude error quaternion
         * @param angularVelocity angular velocity (from IMU)
         * @param control control actions (3-array)
         *
         */
        void controlAction(
            Quaternion &attitudeError,
            const float *angularVelocity,
            float *control);

        /**
         * @brief PWM signals to the four motors
         *
         * @param attitudeError attitude error quaternion
         * @param angularVelocity angular velocity (from IMU)
         * @param throttle throttle signal (between 1000 and 2000)
         * @param motorFL signal to front left motor
         * @param motorFR signal to front right motor
         * @param motorBL  signal to back left motor
         * @param motorBR signal to back right motor
         * @param controlToPwmScaling (optional) scaling parameter
         * @param motorClipLow (optional) lowest value of motor signal [default: 1000]
         * @param motorClipHigh highest value of motor signal [default: 2000]
         */
        void motorPwmSignals(
            Quaternion &attitudeError,
            const float *angularVelocity,
            float throttle,
            int &motorFL,
            int &motorFR,
            int &motorBL,
            int &motorBR,
            float controlToPwmScaling = U_TO_PWM,
            int motorClipLow = ZERO_ROTOR_SPEED,
            int motorClipHigh = ABSOLUTE_MAX_PWM);

    }; /* end of class Controller */

} /* end of namespace bzzz */

#endif /* CONTROLLER_H */

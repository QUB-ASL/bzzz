#include "config.hpp"

#ifndef CONTROLLER_H
#define CONTROLLER_H

// I have the impression that "#pragma once" is not
// supported on ESP32

namespace bzzz
{

    class Quaternion
    {
    private:
        float quaternion[4] = {0};

    public:
        Quaternion()
        {
            quaternion[0] = 1.;
            quaternion[1] = 0.;
            quaternion[2] = 0.;
            quaternion[3] = 0.;
        }

        Quaternion(float *q)
        {
            quaternion[0] = q[0];
            quaternion[1] = q[1];
            quaternion[2] = q[2];
            quaternion[3] = q[3];
        }

        Quaternion(float yaw, float pitch, float roll)
        {
            float cr = cos(roll * 0.5);
            float sr = sin(roll * 0.5);
            float cp = cos(pitch * 0.5);
            float sp = sin(pitch * 0.5);
            float cy = cos(yaw * 0.5);
            float sy = sin(yaw * 0.5);
            quaternion[0] = cr * cp * cy + sr * sp * sy;
            quaternion[1] = sr * cp * cy - cr * sp * sy;
            quaternion[2] = cr * sp * cy + sr * cp * sy;
            quaternion[3] = cr * cp * sy - sr * sp * cy;
        }

        float &operator[](std::size_t idx)
        {
            return quaternion[idx];
        }

        friend Quaternion operator-(Quaternion &lhs, Quaternion &rhs)
        {
            Quaternion diff;
            diff[0] = lhs[0] * rhs[0] + lhs[1] * rhs[1] + lhs[2] * rhs[2] + lhs[3] * rhs[3];
            diff[1] = lhs[0] * rhs[1] - lhs[1] * rhs[0] - lhs[2] * rhs[3] + lhs[3] * rhs[2];
            diff[2] = -lhs[0] * rhs[2] + lhs[1] * rhs[3] + lhs[2] * rhs[0] - lhs[3] * rhs[1];
            diff[3] = -lhs[0] * rhs[3] - lhs[1] * rhs[2] + lhs[2] * rhs[1] + lhs[3] * rhs[0];
            // TODO normalise the result
            return diff;
        }
    };

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
    };
}
#endif /* CONTROLLER_H */

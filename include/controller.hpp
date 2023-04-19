#include "config.hpp"

#ifndef CONTROLLER_H
#define CONTROLLER_H

// I have the impression that "#pragma once" is not
// supported on ESP32

namespace bzzz
{

    class Quaternion {
    public:
        float quaternion[4] = {0};
       
        Quaternion(){
            quaternion[0] = 1.;
            quaternion[1] = 0.;
            quaternion[2] = 0.;
            quaternion[3] = 0.;
        }

        Quaternion(float* q){
            quaternion[0] = q[0];
            quaternion[1] = q[1];
            quaternion[2] = q[2];
            quaternion[3] = q[3];
        }

        Quaternion(float yaw, float pitch, float roll){
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
        
        float& operator[](std::size_t idx) {
            return quaternion[idx];
        }

        friend Quaternion operator-(Quaternion& lhs, Quaternion& rhs){
            Quaternion diff;
            diff[0] =   lhs[0] * rhs[0] + lhs[1] * rhs[1] + lhs[2] * rhs[2] + lhs[3] * rhs[3];
            diff[1] =   lhs[0] * rhs[1] - lhs[1] * rhs[0] - lhs[2] * rhs[3] + lhs[3] * rhs[2];
            diff[2] = - lhs[0] * rhs[2] + lhs[1] * rhs[3] + lhs[2] * rhs[0] - lhs[3] * rhs[1];
            diff[3] = - lhs[0] * rhs[3] - lhs[1] * rhs[2] + lhs[2] * rhs[1] + lhs[3] * rhs[0];
            // TODO normalise the result
            return diff;
        }
    };

    class Controller {
        private:
            float quaternionGain[3] = {-17., -17., -0.98};
            float angularVelocityGain[3] = {-1.4, -1.55, -1.08};
            
        public:
            Controller();

            /**
             * @brief computes control action
             *
             * @param systemState state of the system
             *
             * @return control voltage
             */
            void controlAction(
                    Quaternion& attitudeError,
                    const float* angularVelocity,
                    float* control
                    );
    };
}
#endif /* CONTROLLER_H */

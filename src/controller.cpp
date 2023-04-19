#include "controller.hpp"
#include <math.h>

namespace bzzz
{

    Controller::Controller(){};

    void Controller::controlAction(
            Quaternion& attitudeError,
            const float* angularVelocity,
            float* control) 
    {        
        
        for (int i=0; i<3; i++){
            control[i] = quaternionGain[i] * attitudeError[i+1] 
                + angularVelocityGain[i] * angularVelocity[i];
        }

    }

}
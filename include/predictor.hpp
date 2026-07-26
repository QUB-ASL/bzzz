#pragma once
#include "quaternion.hpp"

namespace bzzz {


/**
 * @brief Vehicle rotational state.
 */
struct VehicleState {
    Quaternion attitude;
    float omega[3];
};

/**
 * @brief Actuator effectiveness matrix Γ.
 *
 * gamma = 1.0  -> healthy actuator
 * gamma = 0.0  -> complete failure
 * 0 < gamma < 1 -> partial loss of effectiveness
 */
struct ActuatorHealth
{
    float gamma[6];

    ActuatorHealth()
    {
        for(int i = 0; i < 6; i++)
            gamma[i] = 1.0f;
    }
};

/**
 * @brief Vehicle dynamics predictor.
 *
 * Implements
 *      x(k+1)=f(x(k), Γu(k))
 */
class VehiclePredictor
{
public:

    VehicleState predict(
        const VehicleState& current,
        const float motorCommand[6],
        const ActuatorHealth& health,
        float dt
    );

};

}
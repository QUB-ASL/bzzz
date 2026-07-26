#pragma once

#include "predictor.hpp"

namespace bzzz
{

struct Residual
{
    Quaternion attitude_error;
    float omega_error[3];
};

class ResidualGenerator
{
public:

    Residual compute(
        const VehicleState& measured,
        const VehicleState& predicted);

};

}
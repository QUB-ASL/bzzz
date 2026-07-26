#include "cost.hpp"

namespace bzzz
{

float ResidualCost::compute(const Residual& r)
{
    float J = 0.0f;

    J += r.attitude_error[0] * r.attitude_error[0];
    J += r.attitude_error[1] * r.attitude_error[1];
    J += r.attitude_error[2] * r.attitude_error[2];
    J += r.attitude_error[3] * r.attitude_error[3];

    for(int i = 0; i < 3; i++)
    {
        J += r.omega_error[i] * r.omega_error[i];
    }

    return J;
}

}
#include "residual.hpp"

namespace bzzz
{

Residual ResidualGenerator::compute(
    const VehicleState& measured,
    const VehicleState& predicted)
{
    Residual r;

    r.attitude_error[0] =
        measured.attitude[0] -
        predicted.attitude[0];

    r.attitude_error[1] =
        measured.attitude[1] -
        predicted.attitude[1];

    r.attitude_error[2] =
        measured.attitude[2] -
        predicted.attitude[2];

    r.attitude_error[3] =
        measured.attitude[3] -
        predicted.attitude[3];

    for(int i = 0; i < 3; i++)
    {
        r.omega_error[i] =
            measured.omega[i] -
            predicted.omega[i];
    }

    return r;
}

}
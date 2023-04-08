#include "controller.h"
#include <math.h>

float control_action(float state_x)
{
    float unconstrained_voltage = c_lqr_gain[0] * state_x + c_lqr_gain[1];
    return fmax(fmin(unconstrained_voltage, c_max_control_action), c_min_control_action);
}
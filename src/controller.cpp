#include "controller.hpp"
#include <math.h>

namespace bzzz
{

    // Note that these variables use the prefix `s_` as they
    // are static (accessible only within this file)

    static const float s_lqrGain[3] = {1.0, 2.0, 3.0}; /**< LQR Gain */
    static const float s_maxControlAction = 10.;       /**< Minimum control action */
    static const float s_minControlAction = -10.;      /**< Maximum control action */

    float controlAction(float systemState)
    {
        float unconstrainedVoltage = s_lqrGain[0] * systemState + s_lqrGain[1];
        return fmax(fmin(unconstrainedVoltage, s_maxControlAction), s_minControlAction);
    }
}
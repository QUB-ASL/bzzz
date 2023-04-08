#include "config.hpp"

namespace bzzz
{

    /**
     * @brief setup of the IMU
     */
    void setupImu(void);

    /**
     * @brief pre-flight calibration
     */
    void preflightCalibrateImu(void);

    /**
     * @brief retrieved the quaternion
     *
     * @param q pointer to 4-array where to store the quaternion
     */
    void quaternion(float *q);

}

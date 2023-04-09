#include "config.hpp"

namespace bzzz
{

    /**
     * @brief setup of the IMU
     *
     * @return true iff the setup of the IMU is successful
     */
    bool setupImu(void);

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

    /**
     * @brief checks for updated measurements from the IMU
     *
     * This function should be called before calling `quaternion`
     *
     * @return true if an updated measurement is available
     */
    bool updateImu(void);

}

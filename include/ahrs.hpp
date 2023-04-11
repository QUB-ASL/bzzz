#include "config.hpp"
#include "MPU9250.h"

namespace bzzz
{

    class AHRS
    {

    private:
        /**
         * MPU9250 object
         */
        MPU9250 m_imu;

    public:
        /**
         * Construct a new instance of AHRS
         */
        AHRS();

        /**
         * @brief setup of the IMU
         *
         * @return true iff the setup of the IMU is successful
         */
        bool setup(void);

        /**
         * @brief pre-flight calibration
         *
         * @param calibrateMagnetometer whether to calibrate the magnetometer
         */
        void preflightCalibrate(bool calibrateMagnetometer = false);

        /**
         * @brief retrieved the quaternion
         *
         * The IMU is positioned upside down, so we need to perform
         * the linear transformation
         *
         * qw' = -qy
         * qx' = -qz
         * qy' = qw
         * qz' = qx
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
        bool update();

/*
 * While flying we will not need to access the Euler angles,
 * so the following is available only in debug mode.
 * This can be activated by passing the build flag -BZZZ_DEBUG
 * in platformio.ini
 */
#ifdef BZZZ_DEBUG
        /**
         * @brief Compute the Euler angles in radians
         *
         * @param euler pointer to array of length 3 where the Euler
         *              angles should be stored (yaw, pitch, roll)
         */
        void eulerAngles(float *euler);
#endif /* BZZZ_DEBUG */

    }; /* end of AHRS class */

}

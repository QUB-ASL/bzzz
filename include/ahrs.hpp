#include "config.hpp"
#include "MPU9250.h"

#ifndef AHRS_H
#define AHRS_H

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
         * @brief calibrate the magnetometer
         *
         * The biases and scaling parameters are computed by `preflightCalibrate`
         *
         * @param biasX magnetometer X-bias
         * @param biasY magnetometer Y-bias
         * @param biasZ magnetometer Z-bias
         * @param scaleX magnetometer X-axis scaling
         * @param scaleY magnetometer Y-axis scaling
         * @param scaleZ magnetometer Z-axis scaling
         */
        void calibrateMagnetometer(float biasX, float biasY, float biasZ,
                                   float scaleX, float scaleY, float scaleZ);
        /**
         * @brief retrieves the quaternion
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
         * @brief angular velocity in rad/s
         *
         * @param w angular velocity vector (3-array)
         *
         */
        void angularVelocity(float *w);

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
 * This can be activated by passing the build flag -DBZZZ_DEBUG
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

} /* end of namespace bzzz */

#endif /* AHRS_H */
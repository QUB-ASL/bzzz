#include "config.hpp"
#include "quaternion.hpp"
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

        /**
         * Discarm AHRS measurements
         *
         * It is a good idea to discard the first few estimates of the IMU
         * to make sure the estimtor has converged
         *
         * @param numMeasurements number of measurements to discard
         *                        Default: 5,000.
         */
        void discardImuMeasurements(size_t numMeasurements = 5000);

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
        void preflightCalibrate(bool calibrateMagnetometer = false);

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

        /**
         *
         * Determine the average quaternion
         *
         * It can be used to determine the initial attitude of the quadcopter.
         *
         * @param avQuaternion reference to quaternion; this is where the result
         *                     should be stored
         * @param windowLength number of measurements to be used to compute the
         *                     average quaternion. Default: 50
         * @param numDiscardMeasurements number of measurements to be discarded
         *                     before starting to collect measurements.
         *                     Default: 10,000
         */
        void averageQuaternion(
            Quaternion &avQuaternion,
            size_t windowLength = 50,
            size_t numDiscardMeasurements = 10000);

        /**
         * 
         * Determine the average angular velocities.
         * 
         * It can be used to determine the average angular velocities of the quadcopter.
         * 
         * @param averageAngularVelocity reference to angular velocites; 
         *                     this is where the result should be stored
         * @param windowLength number of measurements to be used to compute the
         *                     average quaternion. Default: 50
         * @param numDiscardMeasurements number of measurements to be discarded
         *                     before starting to collect measurements.
         *                     Default: 100 (as it is called after averageQuaternion)
         */
        void averageAngularVelocities(
            float *averageAngularVelocity,
            size_t windowLength = 50,
            size_t numDiscardMeasurements = 100); 

        /**
         * Get the current yaw in radians
         * @return the current yaw in radians 
        */
        float currentYawRad();

        /**
         * Get the accelerometer values
         * @param accValues float array pointer of size 3 to store ax, ay, and az values
        */
        void getAccelerometerValues(float *accValues);


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
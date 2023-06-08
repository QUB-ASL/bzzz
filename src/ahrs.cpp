#include "ahrs.hpp"
#include "util.hpp"

namespace bzzz
{

    AHRS::AHRS(){};

    bool AHRS::setup(void)
    {
        Wire.begin();
        delay(2000);

        MPU9250Setting setting;
        setting.accel_fs_sel = ACCEL_FS_SEL::A16G;
        setting.gyro_fs_sel = GYRO_FS_SEL::G2000DPS;
        setting.mag_output_bits = MAG_OUTPUT_BITS::M16BITS;
        // set the frequency of the IMU and the filter
        setting.fifo_sample_rate = FIFO_SAMPLE_RATE::SMPL_250HZ;
        setting.gyro_fchoice = 0x03;
        setting.gyro_dlpf_cfg = GYRO_DLPF_CFG::DLPF_41HZ;
        setting.accel_fchoice = 0x01;
        setting.accel_dlpf_cfg = ACCEL_DLPF_CFG::DLPF_45HZ;

        return m_imu.setup(IMU_ADDRESS, setting);
    }

    void AHRS::calibrateMagnetometer(float biasX, float biasY, float biasZ,
                                     float scaleX, float scaleY, float scaleZ)
    {
        m_imu.setMagBias(biasX, biasY, biasZ);
        m_imu.setMagScale(scaleX, scaleY, scaleZ);
    }

    void AHRS::preflightCalibrate(bool calibrateMagnetometer /* =false */)
    {
        logSerial(LogVerbosityLevel::Info, "[AHRS] stay still; calibrating the accelerometer");
        m_imu.calibrateAccelGyro();
        if (calibrateMagnetometer)
        {
            logSerial(LogVerbosityLevel::Info, "[AHRS] rock and roll; calibrating the magnetometer");
            m_imu.calibrateMag();
            bzzz::logSerial(bzzz::LogVerbosityLevel::Info, "Magnetometer biases: [%.3f, %.3f, %.3f]",
                            m_imu.getMagBiasX(), m_imu.getMagBiasY(), m_imu.getMagBiasZ());
            bzzz::logSerial(bzzz::LogVerbosityLevel::Info, "Magnetometer scaling: [%.3f, %.3f, %.3f]",
                            m_imu.getMagScaleX(), m_imu.getMagScaleY(), m_imu.getMagScaleZ());
        }
    }

    void AHRS::quaternion(float *q)
    {
        q[0] = -m_imu.getQuaternionY();
        q[1] = -m_imu.getQuaternionZ();
        q[2] = m_imu.getQuaternionW();
        q[3] = -m_imu.getQuaternionX();
    }

    void AHRS::angularVelocity(float *w)
    {
        w[0] = m_imu.getGyroX();
        w[1] = m_imu.getGyroY();
        w[2] = -m_imu.getGyroZ();
    }

    bool AHRS::update()
    {
        return m_imu.update();
    }

    void AHRS::discardImuMeasurements(size_t numMeasurements)
    {
        for (int i = 0; i < numMeasurements; i++)
        {
            update();
        }
    }

    void AHRS::averageQuaternion(
        Quaternion &avQuaternion,
        size_t windowLength,
        size_t numDiscardMeasurements)
    {
        float quatInitTemp[4] = {0};
        float averageQuaternion[4] = {0}; // 3D quaternion (x, y, z)

        logSerial(LogVerbosityLevel::Info, "[AHRS] getting ready; discarding measurements");

        // make sure the estimator has converged; discard initial measurements
        discardImuMeasurements(numDiscardMeasurements);

        for (int i = 0; i < windowLength; i++)
        {
            update();
            quaternion(quatInitTemp);
            averageQuaternion[0] += quatInitTemp[0];
            averageQuaternion[1] += quatInitTemp[1];
            averageQuaternion[2] += quatInitTemp[2];
            averageQuaternion[3] += quatInitTemp[3];
        }
        averageQuaternion[0] /= (float)windowLength;
        averageQuaternion[1] /= (float)windowLength;
        averageQuaternion[2] /= (float)windowLength;
        averageQuaternion[3] /= (float)windowLength;

        float normAverageQuaternion =
            sqrt(sq(averageQuaternion[0]) + sq(averageQuaternion[1]) + sq(averageQuaternion[2]) + sq(averageQuaternion[3]));

        avQuaternion[0] = averageQuaternion[0] / normAverageQuaternion;
        avQuaternion[1] = averageQuaternion[1] / normAverageQuaternion;
        avQuaternion[2] = averageQuaternion[2] / normAverageQuaternion;
        avQuaternion[3] = averageQuaternion[3] / normAverageQuaternion;
    }

    void AHRS::averageAngularVelocities(
        float averageAngularVelocity[3],
        size_t windowLength,
        size_t numDiscardMeasurements)
    {
        float angularVelocityTemp[3] = {0};

        logSerial(LogVerbosityLevel::Info, "[AHRS] getting ready; discarding measurements");

        // make sure the estimator has converged; discard initial measurements
        discardImuMeasurements(numDiscardMeasurements);

        for (int i = 0; i < windowLength; i++)
        {
            update();
            angularVelocity(angularVelocityTemp);
            averageAngularVelocity[0] += angularVelocityTemp[0];
            averageAngularVelocity[1] += angularVelocityTemp[1];
            averageAngularVelocity[2] += angularVelocityTemp[2];
        }
        averageAngularVelocity[0] /= (float)windowLength;
        averageAngularVelocity[1] /= (float)windowLength;
        averageAngularVelocity[2] /= (float)windowLength;
    }

    float AHRS::currentYawRad()
    {
        // copied from below
        float q[4] = {0};
        quaternion(q);

        float sinr_cosp = 2 * (q[0] * q[1] + q[2] * q[3]);
        float cosr_cosp = 1 - 2 * (q[1] * q[1] + q[2] * q[2]);
        return std::atan2(sinr_cosp, cosr_cosp);
    }

#ifdef BZZZ_DEBUG
    void AHRS::eulerAngles(float *euler)
    {
        float q[4] = {0};
        quaternion(q);

        float sinr_cosp = 2 * (q[0] * q[1] + q[2] * q[3]);
        float cosr_cosp = 1 - 2 * (q[1] * q[1] + q[2] * q[2]);
        euler[2] = std::atan2(sinr_cosp, cosr_cosp);

        // pitch (y-axis rotation)
        float sinp = std::sqrt(1 + 2 * (q[0] * q[2] - q[1] * q[3]));
        float cosp = std::sqrt(1 - 2 * (q[0] * q[2] - q[1] * q[3]));
        euler[1] = 2 * std::atan2(sinp, cosp) - M_PI / 2;

        // yaw (z-axis rotation)
        float siny_cosp = 2 * (q[0] * q[3] + q[1] * q[2]);
        float cosy_cosp = 1 - 2 * (q[2] * q[2] + q[3] * q[3]);
        euler[0] = std::atan2(siny_cosp, cosy_cosp);
    }
#endif /* BZZZ_DEBUG */

} // namespace bzzz

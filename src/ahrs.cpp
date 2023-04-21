#include "ahrs.hpp"

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
        Serial.println("[AHRS] stay still; calibrating the accelerometer");
        m_imu.calibrateAccelGyro();
        if (calibrateMagnetometer)
        {
            Serial.println("[AHRS] rock and roll; calibrating the magnetometer");
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
        q[3] = m_imu.getQuaternionX();
    }

    void AHRS::angularVelocity(float *w)
    {
        w[0] = m_imu.getGyroX();
        w[1] = m_imu.getGyroY();
        w[2] = m_imu.getGyroZ();
    }

    bool AHRS::update()
    {
        return m_imu.update();
    }

#ifdef BZZZ_DEBUG
    void AHRS::eulerAngles(float *euler)
    {
        float qw = -m_imu.getQuaternionY();
        float qx = -m_imu.getQuaternionZ();
        float qy = m_imu.getQuaternionW();
        float qz = m_imu.getQuaternionX();

        float sinr_cosp = 2 * (qw * qx + qy * qz);
        float cosr_cosp = 1 - 2 * (qx * qx + qy * qy);
        euler[2] = std::atan2(sinr_cosp, cosr_cosp);

        // pitch (y-axis rotation)
        float sinp = std::sqrt(1 + 2 * (qw * qy - qx * qz));
        float cosp = std::sqrt(1 - 2 * (qw * qy - qx * qz));
        euler[1] = 2 * std::atan2(sinp, cosp) - M_PI / 2;

        // yaw (z-axis rotation)
        float siny_cosp = 2 * (qw * qz + qx * qy);
        float cosy_cosp = 1 - 2 * (qy * qy + qz * qz);
        euler[0] = std::atan2(siny_cosp, cosy_cosp);
    }
#endif /* BZZZ_DEBUG */

} // namespace bzzz

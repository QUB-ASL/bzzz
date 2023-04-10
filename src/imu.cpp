#include "imu.hpp"
#include "MPU9250.h"

namespace bzzz
{
    static MPU9250 s_imu;

    bool setupImu(void)
    {
        Wire.begin();
        delay(2500);

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

        return s_imu.setup(IMU_ADDRESS, setting);
    }

    void quaternion(float *q)
    {
        q[0] = s_imu.getQuaternionW();
        q[1] = s_imu.getQuaternionX();
        q[2] = s_imu.getQuaternionY();
        q[3] = s_imu.getQuaternionZ();
    }

    bool updateImu(void)
    {
        return s_imu.update();
    }

} // namespace bzzz

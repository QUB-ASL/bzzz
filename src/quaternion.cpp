#include "quaternion.hpp"

namespace bzzz
{

    Quaternion::Quaternion()
    {
        m_quaternion[0] = 1.;
        m_quaternion[1] = 0.;
        m_quaternion[2] = 0.;
        m_quaternion[3] = 0.;
    }

    Quaternion::Quaternion(float *q)
    {
        m_quaternion[0] = q[0];
        m_quaternion[1] = q[1];
        m_quaternion[2] = q[2];
        m_quaternion[3] = q[3];
    }

    Quaternion::Quaternion(float yaw, float pitch, float roll)
    {
        float cr = cos(roll * 0.5);
        float sr = sin(roll * 0.5);
        float cp = cos(pitch * 0.5);
        float sp = sin(pitch * 0.5);
        float cy = cos(yaw * 0.5);
        float sy = sin(yaw * 0.5);
        m_quaternion[0] = cr * cp * cy + sr * sp * sy;
        m_quaternion[1] = sr * cp * cy - cr * sp * sy;
        m_quaternion[2] = cr * sp * cy + sr * cp * sy;
        m_quaternion[3] = cr * cp * sy - sr * sp * cy;
    }

    float &Quaternion::operator[](std::size_t idx)
    {
        return m_quaternion[idx];
    }

    Quaternion operator-(Quaternion &lhs, Quaternion &rhs)
    {
        Quaternion diff;
        diff[0] = lhs[0] * rhs[0] + lhs[1] * rhs[1] + lhs[2] * rhs[2] + lhs[3] * rhs[3];
        diff[1] = -lhs[0] * rhs[1] + lhs[1] * rhs[0] - lhs[2] * rhs[3] + lhs[3] * rhs[2];
        diff[2] = -lhs[0] * rhs[2] + lhs[1] * rhs[3] + lhs[2] * rhs[0] - lhs[3] * rhs[1];
        diff[3] = -lhs[0] * rhs[3] - lhs[1] * rhs[2] + lhs[2] * rhs[1] + lhs[3] * rhs[0];
        return diff;
    }

} /* end of namespace bzzz */
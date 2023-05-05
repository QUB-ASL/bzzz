#include "config.hpp"

#ifndef QUATERNION_H
#define QUATERNION_H

namespace bzzz
{
    class Quaternion
    {
    private:
        /**
         * Quaternion data (w, x, y, z)
         */
        float m_quaternion[4] = {0};

    public:
        /**
         * @brief Construct a new quaternion
         *
         * q = (1, 0, 0, 0)
         */
        Quaternion();

        /**
         * @brief Construct a quaternion from data
         *
         * @param q a 4-array, (w, x, y, z)
         */
        Quaternion(float *q);

        /**
         * @brief quaternion from NED Euler angles
         *
         * @param yaw yaw angle in rad
         * @param pitch pitch angle in rad
         * @param roll roll angle in rad
         */
        Quaternion(float yaw, float pitch, float roll);

        /**
         * @brief Index operator
         *
         * @param idx index (0-3)
         */
        float &operator[](std::size_t idx);

        /**
         * @brief quaternion difference
         *
         * Hamilton product with conjugate
         *
         * @param lhs left-hand side quaternion
         * @param rhs right-hand side quaternion
         *
         * @return difference of quaternions
         */
        friend Quaternion operator-(Quaternion &lhs, Quaternion &rhs);

    }; /* end of class Quaternion */

} /* end of namespace bzzz */

#endif /* QUATERNION_H */

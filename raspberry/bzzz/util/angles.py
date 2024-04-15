from math import pi, atan2, sqrt  # math functions for calculations

class Angles:

    # function to convert radians to degrees
    def rad2deg(lst):
        """Converts a list of angles in radians to a list of angles in degrees
        :param lst: list of angles in radians
        :return: list of angles in degrees
        """
        return [i*180/pi for i in lst]

    # function to compute quaternions to euler angles
    def euler_angles(q: list):
        """Computes euler angles from given quaternion
        :param q: Quaternion list [q0, q1, q2, q3]
        :return: list of euler angles [yaw, pitch, roll]
        """
        euler_ = [0., 0., 0.]

        sinr_cosp = 2 * (q[0] * q[1] + q[2] * q[3])
        cosr_cosp = 1 - 2 * (q[1] * q[1] + q[2] * q[2])
        euler_[2] = atan2(sinr_cosp, cosr_cosp)

        # pitch (y-axis rotation)
        sinp = sqrt(1 + 2 * (q[0] * q[2] - q[1] * q[3]))
        cosp = sqrt(1 - 2 * (q[0] * q[2] - q[1] * q[3]))
        euler_[1] = 2 * atan2(sinp, cosp) - pi / 2

        # yaw (z-axis rotation)
        siny_cosp = 2 * (q[0] * q[3] + q[1] * q[2])
        cosy_cosp = 1 - 2 * (q[2] * q[2] + q[3] * q[3])
        euler_[0] = atan2(siny_cosp, cosy_cosp)

        return euler_
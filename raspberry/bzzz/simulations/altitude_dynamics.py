import numpy as np


class AltitudeDynamics:
    """The discrete time altitude dynamics of a quad-rotor
    """

    def __init__(self,
                 sampling_time: float = 0.01,
                 initial_altitude: float = 0,
                 initial_velocity_z: float = 0,
                 initial_accleration_z: float = 0,
                 alpha: float = 1,
                 c: float = -9.81):
        """Instantiate altitude dynamics class.
        :param sampling_time: Sampling time of the discrete time system in seconds, defaults to 0.01.
        :param initial_altitude: Initial altitude of the quad-rotor in meters, defaults to 0.
        :param initial_velocity_z: Initial velocity along global z-axis of the quad-rotor in m/s, defaults to 0.
        :param initial_accleration_z: Initial accleration along global z-axis of the quad-rotor in m/s^2, defaults to 0.
        :param alpha: constant of multipilcation to convert reference thrust into accleration in Kg^-1, defaults to 1.
        :param c: Any constant accleration on the drone along the global z-axis (like accleration due to gravity), defaults to -9.81.
        """
        self.Ts = sampling_time
        self.initial_altitude = initial_altitude
        self.initial_velocity_z = initial_velocity_z
        self.initial_accleration_z = initial_accleration_z
        self.alpha = alpha
        self.c = c

        self.altitude_cache = [initial_altitude, ]
        self.velocity_z_cache = [initial_velocity_z, ]
        self.accleration_z_cache = [initial_accleration_z, ]

    def __dynamics(self, altitude_t: float,
                   velocity_z_t: float,
                   thrust_ref_t: float):
        """Discrete time dynamics of the quad-rotor.
        :param altitude_t: Altitude at time t in m, current altitude.
        :param velocity_z_t: Velocity at time t in m/s along global z-axis, current velocity.
        :param thrust_ref_t: Reference thrust/ thrust produced by the quad-rotor along the global z-axis, current thrust.
        :return: altitude, velocity, and accleration updates
        """
        w_z_t, w_vz_t = np.random.normal(loc=0, scale=0.05, size=2)
        altitude_t_1 = altitude_t + self.Ts*velocity_z_t + w_z_t
        accleration_z_t = self.alpha*thrust_ref_t + self.c
        velocity_z_t_1 = velocity_z_t + self.Ts*accleration_z_t + w_vz_t
        return altitude_t_1, velocity_z_t_1, accleration_z_t

    def simulate(self, thrust_ref_t: float):
        """Simulate and update the discrete time altitude states of the quad-rotor.
        :param thrust_ref_t: Reference thrust/ thrust produced by the quad-rotor along the global z-axis, current thrust.
        """
        altitude_t_1, velocity_z_t_1, accleration_z_t = self.__dynamics(
            altitude_t=self.altitude_cache[-1], velocity_z_t=self.velocity_z_cache[-1], thrust_ref_t=thrust_ref_t)
        self.altitude_cache.append(altitude_t_1)
        self.velocity_z_cache.append(velocity_z_t_1)
        self.accleration_z_cache.append(accleration_z_t)

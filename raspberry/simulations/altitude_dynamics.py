import numpy as np

class AltitudeDynamics:
    """The discrete time altitude dynamics of a quad-rotor
    """
    def __init__(self, sampling_time: float = 0.01, initial_altitude: float = 0, vz_0: float = 0, az_0: float = 0, alpha: float = 1, c: float = -9.81):
        """Instantiate altitude dynamics class.
        :param sampling_time: Sampling time of the discrete time system in seconds, defaults to 0.01.
        :param initial_altitude: Initial altitude of the quad-rotor in meters, defaults to 0.
        :param vz_0: Initial velocity along global z-axis of the quad-rotor in m/s, defaults to 0.
        :param az_0: Initial accleration along global z-axis of the quad-rotor in m/s^2, defaults to 0.
        :param alpha: constant of multipilcation to convert reference thrust into accleration in Kg^-1, defaults to 1.
        :param c: Any constant accleration on the drone along the global z-axis (like accleration due to gravity), defaults to -9.81.
        """
        self.Ts = sampling_time
        self.initial_altitude = initial_altitude
        self.vz_0 = vz_0
        self.az_0 = az_0
        self.alpha = alpha
        self.c = c

        self.z = [initial_altitude, ]
        self.vz = [vz_0, ]
        self.az = [az_0, ]

    def __dynamics(self, z_t: float, vz_t: float, Tref_t: float):
        """Discrete time dynamics of the quad-rotor.
        :param z_t: Altitude at time t in mts, current altitude.
        :param vz_t: Velocity at time t in m/s along global z-axis, current velocity.
        :param Tref_t: Reference thrust/ thrust produced by the quad-rotor along the global z-axis, current thrust.
        :return: altitude, velocity, and accleration updates
        """
        w_z_t, w_vz_t =   np.random.normal(loc=0, scale=0.05, size=2)
        z_t_1 = z_t + self.Ts*vz_t + w_z_t
        az_t = self.alpha*Tref_t + self.c
        vz_t_1 = vz_t + self.Ts*az_t + w_vz_t
        return z_t_1, vz_t_1, az_t

    def simulate(self, Tref_t: float):
        """Simulate and update the discrete time altitude states of the quad-rotor.
        :param Tref_t: Reference thrust/ thrust produced by the quad-rotor along the global z-axis, current thrust.
        """
        z_t_1, vz_t_1, az_t = self.__dynamics(z_t=self.z[-1], vz_t=self.vz[-1], Tref_t=Tref_t)
        self.z.append(z_t_1)
        self.vz.append(vz_t_1)
        self.az.append(az_t)

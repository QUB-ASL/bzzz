import numpy as np
from osqp import OSQP
import control as ctrl
from scipy import sparse
import matplotlib.pyplot as plt
from scipy.linalg import block_diag
from threading import Thread, Lock
from gnss import Gnss  
import math
import time

class MPCController:
    """MPC for drone navigation.
    The system dynamics are time-invariant but the controller accounts for changing GPS coordinates.
    This implementation of MPC uses the OSQP solver for quadratic programming.
    """

    def __init__(self, sampling_frequency=50, gravity=9.8, acceleration_coefficient_x=1, acceleration_coefficient_y=1, prediction_horizon=25, max_velocity=5, gnss_update_interval=1):
        """Constructor

        :param sampling_frequency: Sampling frequency in Hz, defaults to 50
        :param gravity: Gravity acceleration in m/s^2, defaults to 9.8
        :param acceleration_coefficient_x: Acceleration coefficient in x direction, defaults to 1
        :param acceleration_coefficient_y: Acceleration coefficient in y direction, defaults to 1
        :param prediction_horizon: MPC prediction horizon, defaults to 25
        :param max_velocity: Maximum velocity in m/s, defaults to 5
        :param gnss_update_interval: GNSS update interval in seconds, defaults to 1
        """
        # Calculate sampling time from frequency
        self.__Ts = 1 / sampling_frequency

        # Store system parameters
        self.__g = gravity
        self.__Ax = acceleration_coefficient_x
        self.__Ay = acceleration_coefficient_y
        self.__N = prediction_horizon
        self.__max_velocity = max_velocity
        self.__gnss_update_interval = gnss_update_interval

        # Initialize GNSS module
        self.__gnss = Gnss()

        # Construct system dynamics matrices
        self.__A, self.__B, self.__C, self.__D = self.__construct_system_matrices()

        # Get state and input dimensions from system matrices
        self.__nx = self.__A.shape[1]  # Number of states
        self.__nu = self.__B.shape[1]  # Number of inputs

        # Define weight matrices for the cost function
        self.__Q = np.diag([10, 10, 1, 1])  # State cost (prioritize position over velocity)
        self.__R = np.diag([0.1, 0.1])      # Input cost (small penalty on control effort)

        # Construct MPC-specific matrices
        self.__A_cal, self.__B_cal, self.__Q_boldface, self.__R_boldface = self.__construct_mpc_matrices()

        # Set up the quadratic cost matrix for OSQP
        self.__P = sparse.csc_matrix(2 * (self.__B_cal.T @ self.__Q_boldface @ self.__B_cal + self.__R_boldface))
        self.__q = None  # Linear cost term, will be updated in each iteration

        # Set up constraint matrices for OSQP
        self.__F_constraint = sparse.vstack([
            sparse.eye(2*self.__N),  # Input constraints
            sparse.kron(sparse.eye(self.__N), np.array([[1, 0], [-1, 0], [0, 1], [0, -1]]))  # Velocity constraints
        ])
        self.__velocity_max = self.__max_velocity * np.ones(4*self.__N)
        self.__u_max = np.inf * np.ones(2*self.__N)  # No limit on acceleration
        self.__u_min = -np.inf * np.ones(2*self.__N)
        self.__l = np.hstack([self.__u_min, -self.__velocity_max])
        self.__u = np.hstack([self.__u_max, self.__velocity_max])

        # Initialize OSQP solver
        self.__osqp = OSQP()
        self.__osqp.setup(P=self.__P, q=self.__q, A=self.__F_constraint, l=self.__l, u=self.__u, warm_start=True)

        # Initialize thread-related attributes
        self.__lock = Lock()
        self.__thread = Thread(target=self.__run_mpc_in_background)
        self.__keep_going = True

        # Initialize state estimation variables
        self.__state_estimate = np.zeros(4)
        self.__last_x = 0
        self.__last_y = 0

        # Initialize location attributes
        self.__initial_lat = None
        self.__initial_lon = None
        self.__target_lat = None
        self.__target_lon = None

        # Flag to indicate if initial position has been set
        self.__initial_position_set = False

    def __construct_system_matrices(self):
        """Construct the system matrices A, B, C, and D.
        
        The system is modeled as:
        x[k+1] = A*x[k] + B*u[k]
        y[k] = C*x[k] + D*u[k]
        
        where x = [x, y, vx, vy]^T and u = [ax, ay]^T
        """
        # State transition matrix
        A = np.array([
            [1, 0, self.__Ts, 0],           # x position
            [0, 1, 0, self.__Ts],           # y position
            [0, 0, 1-self.__Ts*self.__Ax, 0],  # x velocity (with drag)
            [0, 0, 0, 1-self.__Ts*self.__Ay]   # y velocity (with drag)
        ])
        
        # Input matrix
        B = np.array([
            [0, 0],                 # x position doesn't change directly with acceleration
            [0, 0],                 # y position doesn't change directly with acceleration
            [self.__Ts, 0],         # x velocity changes with x acceleration
            [0, self.__Ts]          # y velocity changes with y acceleration
        ])
        
        C = np.eye(4)  # We can measure all states directly
        D = np.zeros((4, 2))  # No feed-forward term
        
        return A, B, C, D

    def __construct_mpc_matrices(self):
        """Construct the MPC matrices A_cal, B_cal, Q_boldface, and R_boldface.
        
        These matrices are used to formulate the MPC optimization problem.
        """
        # Compute powers of A for prediction
        A_cal = np.vstack([np.linalg.matrix_power(self.__A, i) for i in range(1, self.__N+1)])

        # Construct B_cal for input prediction
        B_cal = np.zeros((self.__N * self.__nx, self.__nu * self.__N))
        for i in range(self.__N):
            for j in range(i + 1):
                B_cal[i*self.__nx:(i+1)*self.__nx, j*self.__nu:(j+1)*self.__nu] = np.linalg.matrix_power(self.__A, i-j) @ self.__B

        # Construct block diagonal Q and R matrices for the entire prediction horizon
        Q_boldface = block_diag(*([self.__Q] * self.__N))
        R_boldface = block_diag(*([self.__R] * self.__N))

        return A_cal, B_cal, Q_boldface, R_boldface

    def __run_mpc_in_background(self):
        """Run the MPC controller in the background.
        
        This method is executed in a separate thread to continuously update the control action.
        """
        while self.__keep_going:
            with self.__lock:
                if not self.__initial_position_set:
                    self.__set_initial_location_from_gnss()
                else:
                    current_state = self.__get_current_state()
                    target_state = self.__get_target_state()
                    u = self.get_control_action(current_state, target_state)
                    self.__update_state_estimate(u)
            time.sleep(self.__gnss_update_interval)

    def __set_initial_location_from_gnss(self):
        """Set the initial location based on the first GNSS reading."""
        lat, lon = self.__gnss.latitude, self.__gnss.longitude
        if lat is not None and lon is not None:
            self.__initial_lat = lat
            self.__initial_lon = lon
            self.__last_x = 0
            self.__last_y = 0
            self.__state_estimate = np.array([0, 0, 0, 0])  # Initialize at origin with zero velocity
            self.__initial_position_set = True
            print(f"Initial position set to: Lat {self.__initial_lat}, Lon {self.__initial_lon}")

    def __get_current_state(self):
        """Get the current state from GNSS data.
        
        Converts GNSS latitude and longitude to local x, y coordinates and estimates velocity.
        """
        lat, lon = self.__gnss.latitude, self.__gnss.longitude
        # Convert to local coordinates (assuming flat Earth for simplicity)
        x = (lon - self.__initial_lon) * 111000 * np.cos(np.radians(self.__initial_lat))
        y = (lat - self.__initial_lat) * 111000
        # Estimate velocity using finite difference
        vx = (x - self.__last_x) / self.__gnss_update_interval
        vy = (y - self.__last_y) / self.__gnss_update_interval
        self.__last_x, self.__last_y = x, y
        return np.array([x, y, vx, vy])

    def __get_target_state(self):
        """Get the target state.
        
        Converts target latitude and longitude to local x, y coordinates.
        """
        x = (self.__target_lon - self.__initial_lon) * 111000 * np.cos(np.radians(self.__initial_lat))
        y = (self.__target_lat - self.__initial_lat) * 111000
        return np.array([x, y, 0, 0])  # Target velocity is set to zero

    def __update_state_estimate(self, u):
        """Update the state estimate based on the control action.
        
        This method simulates the drone's movement between GNSS updates.
        """
        self.__state_estimate = self.__A @ self.__state_estimate + self.__B @ u

    def get_control_action(self, current_state, target_state):
        """Calculate and return the control action.

        :param current_state: current state [x, y, vx, vy]
        :param target_state: target state [x, y, vx, vy]
        :return: control action [ax, ay]
        """
        # Compute the state error
        state_error = current_state - target_state
        
        # Update the linear cost term
        q = 2 * self.__B_cal.T @ self.__Q_boldface @ (self.__A_cal @ state_error)
        
        # Update the OSQP problem
        self.__osqp.update(q=q)
        
        # Solve the quadratic program
        res = self.__osqp.solve()
        
        # Return only the first control action
        return res.x[:self.__nu]

    def set_relative_target(self, distance, angle_degrees):
        """Set the target location relative to the current position.

        :param distance: Distance to the target in meters
        :param angle_degrees: Angle to the target in degrees (0 is North, 90 is East)
        """
        if not self.__initial_position_set:
            raise ValueError("Initial position has not been set yet. Wait for the first GNSS reading.")

        # Convert angle to radians
        angle_radians = math.radians(angle_degrees)

        # Calculate the change in latitude and longitude
        delta_lat = distance * math.cos(angle_radians) / 111000  # Approximate degrees latitude per meter
        delta_lon = distance * math.sin(angle_radians) / (111000 * math.cos(math.radians(self.__initial_lat)))  # Approximate degrees longitude per meter

        # Set the new target coordinates
        self.__target_lat = self.__initial_lat + delta_lat
        self.__target_lon = self.__initial_lon + delta_lon

        print(f"Target set to: Lat {self.__target_lat}, Lon {self.__target_lon}")

    def get_current_position(self):
        """Get the current position in latitude and longitude."""
        return self.__gnss.latitude, self.__gnss.longitude

    def get_target_position(self):
        """Get the target position in latitude and longitude."""
        return self.__target_lat, self.__target_lon

    def __enter__(self):
        """Start the background thread when entering a context."""
        self.__thread.start()
        return self

    def __exit__(self, *args):
        """Stop the background thread when exiting a context."""
        self.__keep_going = False
        self.__thread.join()

# test script
if __name__ == '__main__':
    with MPCController() as controller:
        # Wait for the initial position to be set
        while not controller._MPCController__initial_position_set:
            time.sleep(0.1)
        
        print("Initial position:", controller.get_current_position())
        
        # Set target location 1000 meters northeast of the starting point
        controller.set_relative_target(distance=1000, angle_degrees=45)
        
        print("Target position:", controller.get_target_position())
        
        # The controller will now run in the background, continuously updating
        # its trajectory based on new GNSS measurements
        
        # For demonstration purposes, we'll just let it run for a while
        time.sleep(60)  # Run for 60 seconds
        
        # Get final position
        print("Final position:", controller.get_current_position())

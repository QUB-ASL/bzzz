import numpy as np
from osqp import OSQP
import control as ctrl
from scipy import sparse
import matplotlib.pyplot as plt
from scipy.linalg import block_diag
from threading import Thread, Lock
from gnss import Gnss  

class MPCController:
    def __init__(self,
                 Ts=0.02,  # Sampling time
                 g=9.8,    # Gravity
                 Ax=1, Ay=1,  # Acceleration coefficients
                 prediction_horizon=25,
                 max_velocity=5,  # Maximum velocity in m/s
                 gnss_update_interval=1  # GNSS update interval in seconds
                 ):
        
        self.__lock = Lock()
        self.__thread = Thread(target=self.__run_mpc_in_background)
        self.__keep_going = True
        
        # System definitions
        self.Ts = Ts
        self.g = g
        self.Ax = Ax
        self.Ay = Ay
        self.N = prediction_horizon
        self.max_velocity = max_velocity
        self.gnss_update_interval = gnss_update_interval
        
        # Initialize GNSS
        self.gnss = Gnss()
        
        # System matrices
        self.A, self.B, self.C, self.D = self.__construct_system_matrices()
        
        # State and input dimensions
        self.nx = self.A.shape[1]  # Number of states
        self.nu = self.B.shape[1]  # Number of inputs
        
        # Weight matrices for the cost function
        self.Q = np.diag([10, 10, 1, 1])  # State cost
        self.R = np.diag([0.1, 0.1])      # Input cost
        
        # MPC matrices
        self.A_cal, self.B_cal, self.Q_boldface, self.R_boldface = self.__construct_mpc_matrices()
        
        # OSQP setup
        self.P = sparse.csc_matrix(2 * (self.B_cal.T @ self.Q_boldface @ self.B_cal + self.R_boldface))
        self.q = None  # Will be updated in each iteration
        
        # Constraints
        self.F_constraint = sparse.vstack([
            sparse.eye(2*self.N),  # Input constraints
            sparse.kron(sparse.eye(self.N), np.array([[1, 0], [-1, 0], [0, 1], [0, -1]]))  # Velocity constraints
        ])
        self.velocity_max = self.max_velocity * np.ones(4*self.N)
        self.u_max = np.inf * np.ones(2*self.N)  # No limit on acceleration
        self.u_min = -np.inf * np.ones(2*self.N)
        self.l = np.hstack([self.u_min, -self.velocity_max])
        self.u = np.hstack([self.u_max, self.velocity_max])
        
        # Initialize OSQP solver
        self.osqp = OSQP()
        self.osqp.setup(P=self.P, q=self.q, A=self.F_constraint, l=self.l, u=self.u, warm_start=True)
        
        self.__thread.start()

    def __construct_system_matrices(self):
        # State: [x, y, vx, vy]
        # Input: [ax, ay]
        A = np.array([
            [1, 0, self.Ts, 0],
            [0, 1, 0, self.Ts],
            [0, 0, 1-self.Ts*self.Ax, 0],
            [0, 0, 0, 1-self.Ts*self.Ay]
        ])
        
        B = np.array([
            [0, 0],
            [0, 0],
            [self.Ts, 0],
            [0, self.Ts]
        ])
        
        C = np.eye(4)  # We can measure all states
        D = np.zeros((4, 2))
        
        return A, B, C, D

    def __construct_mpc_matrices(self):
        # Calculate A^1 to A^N and concatenate vertically
        A_cal = np.vstack([np.linalg.matrix_power(self.A, i) for i in range(1, self.N+1)])

        # Construct B_cal
        B_cal = np.zeros((self.N * self.nx, self.nu * self.N))
        for i in range(self.N):
            for j in range(i + 1):
                B_cal[i*self.nx:(i+1)*self.nx, j*self.nu:(j+1)*self.nu] = np.linalg.matrix_power(self.A, i-j) @ self.B

        # Construct Q_boldface and R_boldface
        Q_boldface = block_diag(*([self.Q] * self.N))
        R_boldface = block_diag(*([self.R] * self.N))

        return A_cal, B_cal, Q_boldface, R_boldface

    def __run_mpc_in_background(self):
        while self.__keep_going:
            with self.__lock:
                # Get current state from GNSS
                current_state = self.__get_current_state()
                
                # Get target state
                target_state = self.__get_target_state()
                
                # Compute the control action
                u = self.get_control_action(current_state, target_state)
                
                # Apply the control action (in a real system, this would actuate motors)
                # Here, we'll just update our state estimate
                self.__update_state_estimate(u)
            
            # Wait for the next GNSS update
            time.sleep(self.gnss_update_interval)

    def __get_current_state(self):
        # Get current latitude, longitude from GNSS
        lat, lon = self.gnss.latitude, self.gnss.longitude
        
        # Convert to local coordinates (assuming flat Earth for simplicity)
        x = (lon - self.initial_lon) * 111000 * np.cos(np.radians(self.initial_lat))
        y = (lat - self.initial_lat) * 111000
        
        # Estimate velocity (in a real application, you might get this from IMU or GNSS Doppler)
        vx = (x - self.last_x) / self.gnss_update_interval
        vy = (y - self.last_y) / self.gnss_update_interval
        
        self.last_x, self.last_y = x, y
        
        return np.array([x, y, vx, vy])

    def __get_target_state(self):
        # This should return the target state 
        # For now, we'll just return a fixed target
        return np.array([100, 100, 0, 0])  # 100m east, 100m north, zero velocity

    def __update_state_estimate(self, u):
        # Update our state estimate based on the control action
        # In a real system, this would be replaced by actual sensor measurements
        self.state_estimate = self.A @ self.state_estimate + self.B @ u

    def get_control_action(self, current_state, target_state):
        """
        Computes the control action based on the current state and target state.

        :param current_state: current state [x, y, vx, vy]
        :param target_state: target state [x, y, vx, vy]
        :return: control action [ax, ay]
        """
        # Compute the state error
        state_error = current_state - target_state
        
        # Compute the cost function
        q = 2 * self.B_cal.T @ self.Q_boldface @ (self.A_cal @ state_error)
        
        # Update OSQP problem
        self.osqp.update(q=q)
        
        # Solve the QP problem
        res = self.osqp.solve()
        
        # Extract the control action (only the first one, as per MPC principle)
        u = res.x[:self.nu]
        
        return u

    def set_initial_location(self, lat, lon):
        """
        Sets the initial location and initializes the state estimate.
        """
        self.initial_lat = lat
        self.initial_lon = lon
        self.last_x = 0
        self.last_y = 0
        self.state_estimate = np.array([0, 0, 0, 0])  # Start at origin with zero velocity

    def set_target_location(self, lat, lon):
        """
        Sets the target location.
        """
        self.target_lat = lat
        self.target_lon = lon

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.__keep_going = False
        self.__thread.join()

if __name__ == '__main__':
    with MPCController() as controller:
        # Set initial location
        initial_lat, initial_lon = 0, 0  # Replace with actual initial GNSS coordinates
        controller.set_initial_location(initial_lat, initial_lon)
        
        # Set target location
        target_lat, target_lon = 1, 1  # Replace with actual target GNSS coordinates
        controller.set_target_location(target_lat, target_lon)
        
        # The controller will now run in the background, continuously updating
        # its trajectory based on new GNSS measurements
        
        # For demonstration purposes, we'll just let it run for a while
        time.sleep(60)  # Run for 60 seconds

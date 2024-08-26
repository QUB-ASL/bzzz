import numpy as np
from osqp import OSQP
import control as ctrl
from scipy import sparse
import matplotlib.pyplot as plt
from scipy.linalg import block_diag
from threading import Thread, Lock

class MPCController:
    def __init__(self,
                 Ts=0.02,
                 g=9.8,
                 Tr=0.5,
                 Tp=0.7,
                 Td=0.1,
                 Ax=1,
                 Ay=1,
                 Az=1,
                 Kr=1,
                 Kp=1,
                 theta_rd=0.2,
                 theta_pd=0.3,
                 prediction_horizon=25,
                 max_tilt=np.deg2rad(10)):
        
        self.__lock = Lock()
        self.__thread = Thread(target=self.__run_mpc_in_background)
        self.__keep_going = True
        
        # System definitions
        self.Ts = Ts
        self.g = g
        self.Tr = Tr
        self.Tp = Tp
        self.Td = Td
        self.Ax = Ax
        self.Ay = Ay
        self.Az = Az
        self.Kr = Kr
        self.Kp = Kp
        self.theta_rd = theta_rd
        self.theta_pd = theta_pd
        self.N = prediction_horizon
        self.max_tilt = max_tilt
        
        # System matrices
        self.A, self.B, self.C, self.D = self.__construct_system_matrices()
        
        # MPC matrices
        self.A_cal, self.B_cal, self.Q_boldface, self.R_boldface, self.G, self.EB = self.__construct_mpc_matrices()
        
        # OSQP setup
        self.P = sparse.csc_matrix(self.G)
        self.F_constraint = sparse.eye(2*self.N)
        self.tilt_max = self.max_tilt * np.ones(self.N*2, )
        self.tilt_min = -self.max_tilt * np.ones(2*self.N, )
        self.l = self.tilt_min
        self.u = self.tilt_max
        self.osqp = OSQP()
        self.osqp.setup(P=self.P, q=None, A=self.F_constraint, l=self.l, u=self.u, warm_start=True)
        
        self.__thread.start()

    def __construct_system_matrices(self):
        A = np.array([[1, 0, self.Ts, 0, 0, 0],
                      [0, 1, 0, self.Ts, 0, 0],
                      [0, 0, 1-(self.Ts*self.Ax), 0, 0, -self.Ts*self.g],
                      [0, 0, 0, 1-(self.Ts*self.Ay), self.Ts*self.g, 0],
                      [0, 0, 0, 0, 1-(self.Ts/self.Tr), 0],
                      [0, 0, 0, 0, 0, 1-(self.Ts/self.Tp)]])

        B = np.array([[0, 0],
                      [0, 0],
                      [0, 0],
                      [0, 0],
                      [(self.Ts*self.Kr)/self.Tr, 0],
                      [0, (self.Ts*self.Kp)/self.Tp]])

        C = np.array([[1, 0, 0, 0, 0, 0],
                      [0, 1, 0, 0, 0, 0]])
        
        D = np.zeros((2, 2))
        
        return A, B, C, D

    def __construct_mpc_matrices(self):
        nx = self.A.shape[1]
        nu = self.B.shape[1]
        ny = self.C.shape[0]
        I = np.eye(nx)

        # Calculate A^1 to A^N and concatenate vertically
        A_cal = I.copy()
        for n in range(1, self.N):
            A_cal = np.vstack((A_cal, np.linalg.matrix_power(self.A, n)))

        # Initialize B_cal with zeros
        B_cal = np.zeros((self.N * nx, nu * self.N))
        for i in range(self.N):
            for j in range(i + 1):
                result = np.linalg.matrix_power(self.A, i-j) @ self.B
                B_cal[i*nx:(i+1)*nx, j*nu:(j+1)*nu] = result

        # Create a list with Q repeated N times
        Q_list = [self.Q] * self.N
        Q_boldface = block_diag(*Q_list)

        # Create an identity matrix of size N
        I_N = np.eye(self.N)

        # Use the Kronecker product to create R_boldface
        R_boldface = np.kron(I_N, self.R)

        # Calculate G
        G = B_cal.T @ Q_boldface @ B_cal + R_boldface

        # Create constraint matrices
        E_r = sparse.csc_matrix(([1], ([0], [4])), shape=(1, nx))
        E_p = sparse.csc_matrix(([1], ([0], [5])), shape=(1, nx))
        E_rp = sparse.vstack([E_r, E_p])
        E_boldface = sparse.kron(sparse.eye(self.N), E_rp)
        EB = E_boldface @ B_cal

        # Compute G for reference tracking
        W = np.block([[self.A - np.eye(nx), self.B],
                      [self.C, self.D]])
        G = np.linalg.pinv(W) @ np.block([[np.zeros((nx, ny))],
                                          [np.eye(ny)]])

        return A_cal, B_cal, Q_boldface, R_boldface, G, EB

    def __run_mpc_in_background(self):
        x0 = np.array([[25, 1, 0.0, 0.0, 0, 0]]).T  # Initial state
        x = x0
        sim_steps = 2000  # Number of simulation steps
        
        while True:
            with self.__lock:
                # Compute equilibrium point
                xue = self.G @ r
                x_e = xue[:self.nx]
                u_e = xue[self.nx:]

                # Predict state trajectory
                x_pred = np.zeros((self.nx, self.N))
                x_pred[:, 0] = x.flatten()
                for i in range(1, self.N):
                    x_pred[:, i] = self.A @ x_pred[:, i-1]

                # Compute cost function
                q = 2 * self.B_cal.T @ self.Q_boldface @ (self.A_cal @ x - np.tile(x_e, (self.N, 1)))

                # Solve MPC problem
                self.osqp.update(q=q)
                res = self.osqp.solve()

                u_mpc = np.reshape(res.x[:self.nu], (self.nu, 1))
                u = u_e + u_mpc

                # Apply the control input and update the state
                x = self.A @ x + self.B @ u

                # Check if constraints are respected
                roll = x[4, 0]
                pitch = x[5, 0]
                if abs(roll) > self.max_tilt or abs(pitch) > self.max_tilt:
                    print(f"Constraint violated: Roll = {np.rad2deg(roll):.2f}°, Pitch = {np.rad2deg(pitch):.2f}°")

            if not self.__keep_going:
                return

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.__keep_going = False

    def get_control_action(self, x, r):
        """
        Computes the control action based on the current state and reference.

        :param x: current state
        :param r: reference
        :return: control action
        """
        with self.__lock:
            # Compute equilibrium point
            xue = self.G @ r
            x_e = xue[:self.nx]
            u_e = xue[self.nx:]

            # Predict state trajectory
            x_pred = np.zeros((self.nx, self.N))
            x_pred[:, 0] = x.flatten()
            for i in range(1, self.N):
                x_pred[:, i] = self.A @ x_pred[:, i-1]

            # Compute cost function
            q = 2 * self.B_cal.T @ self.Q_boldface @ (self.A_cal @ x - np.tile(x_e, (self.N, 1)))

            # Solve MPC problem
            self.osqp.update(q=q)
            res = self.osqp.solve()

            u_mpc = np.reshape(res.x[:self.nu], (self.nu, 1))
            u = u_e + u_mpc

        return u

if __name__ == '__main__':
    with MPCController() as controller:
        x0 = np.array([[25, 1, 0.0, 0.0, 0, 0]]).T
        x = x0
        for _ in range(2000):
            if _ < 500:
                r = np.array([[30], [5]])
            elif _ < 1000:
                r = np.array([[10], [15]])
            else:
                r = np.array([[15], [10]])
            u = controller.get_control_action(x, r)
            x = controller.A @ x + controller.B @ u
            # Do something with the control action u

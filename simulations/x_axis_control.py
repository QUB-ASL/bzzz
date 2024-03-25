import numpy as np
import matplotlib.pyplot as plt

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.previous_error = 0

    def compute(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt if dt > 0 else 0
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.previous_error = error
        return output

# Simulation parameters
dt = 0.1  # Time step (s)
t_sim = 1000  # Total simulation steps

# PID Controller for both latitude and longitude
pid_lat = PIDController(kp=1, ki=0.1, kd=0.5)
pid_long = PIDController(kp=1, ki=0.1, kd=0.5)

# Initial and target positions (latitude, longitude)
initial_position = np.array([1.002, 1.0004])  # Starting at the origin
target_position = np.array([1.0, 1.0])  # Initial target position

# Initial velocity and position
velocity = np.array([0.0, 0.0])
position = initial_position.copy()

# Lists to store data for plotting
positions = [position.copy()]
velocities = [velocity.copy()]

# wind force
# wind_force = np.array([0.01, -0.02])

# Main simulation loop
current_step = 0  # Track the current simulation step
for _ in range(t_sim):
    current_step += 1  # Increment the current step
    # if current_step > 500 and current_step < 600:  # Change target at step 500
    #     target_position = target_position + [0.0001, -0.001]

    # Compute errors
    error_lat = target_position[0] - position[0]
    error_long = target_position[1] - position[1]

    # Update velocities based on PID output
    velocity[0] = pid_lat.compute(error_lat, dt) 
    velocity[1] = pid_long.compute(error_long, dt) 
    # velocity[0] = pid_lat.compute(error_lat, dt) + wind_force[0]
    # velocity[1] = pid_long.compute(error_long, dt) + wind_force[1]
    
    # wind_force = np.array([0.01 * current_step / t_sim, -0.02 * current_step / t_sim])
    
    # Update position
    position += velocity * dt

    # Store data for plotting
    positions.append(position.copy())
    velocities.append(velocity.copy())

# Convert lists to Numpy arrays for easy plotting
positions = np.array(positions)
velocities = np.array(velocities)

# Plotting
plt.figure(figsize=(14, 6))

# Plot position
plt.subplot(1, 2, 1)
plt.plot(positions[:, 0], positions[:, 1], label='Drone Path')
plt.scatter(*initial_position, color='green', label='Initial Position')
plt.scatter(*target_position, color='red', label='Final Target Position')
plt.scatter(1.0, 1.0, color='orange', label='Initial Target Position')
plt.xlabel('Latitude')
plt.ylabel('Longitude')
plt.title('Drone Path Over Time')
plt.legend()

# Plot velocity
plt.subplot(1, 2, 2)
plt.plot(velocities[:, 0], label='Latitude Velocity')
plt.plot(velocities[:, 1], label='Longitude Velocity')
plt.xlabel('Time Step')
plt.ylabel('Velocity')
plt.title('Velocity Over Time')
plt.legend()

plt.tight_layout()
plt.show()

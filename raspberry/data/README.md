# Data files

CSV files with the following columns:

- `timestamp_ms` timestamp in milliseconds
- `throttle_ref` throttle reference from the RC
- `yaw` yaw angle in rad
- `pitch` pitch angle in rad
- `roll` roll angle in rad
- `tof_measurement` measurement from the ToF sensor in mm
- `accX` acc_x from the accelerometer, in m/s^2
- `accY` acc_y from the accelerometer, in m/s^2 
- `accZ` acc_z from the accelerometer, in m/s^2
- `altitude_ref` altitude reference in m
- `RC data` dump of the RC data as a string - exactly as encoded by the RC parser 
- `mot_FL` PWM signal to the forward left motor (int)
- `mot_FR` PWM signal to the forward right motor (int)
- `mot_BL` PWM signal to the backward left motor (int)
- `mot_BR` PWM signal to the backward right motor (int)
- `KF_altitutde_est` altitude estimate from KF in m
- `KF_velocity_z_est` velocity estimate from KF in m/s
- `KF_alpha_est` KF estimate of alpha
- `KF_beta_est` KF estimate of beta

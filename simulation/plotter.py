import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('test.csv')

df['timestamp'] = pd.to_datetime(df['timestamp'])

# Plot KF_alpha_est
plt.figure(figsize=(12, 6))
plt.plot(df['timestamp'], df['KF_alpha_est'], label='KF_alpha_est')
plt.xlabel('Time')
plt.ylabel('KF_alpha_est')
plt.title('KF_alpha_est over Time')
plt.legend()
plt.show()

# Plot KF_beta_est
plt.figure(figsize=(12, 6))
plt.plot(df['timestamp'], df['KF_beta_est'], label='KF_beta_est')
plt.xlabel('Time')
plt.ylabel('KF_beta_est')
plt.title('KF_beta_est over Time')
plt.legend()
plt.show()

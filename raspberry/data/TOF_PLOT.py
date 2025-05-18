import matplotlib.pyplot as plt 
import pandas as pd

file = pd.read_csv("2024_3_15_at_16h46m37s.csv")
file2 = pd.read_csv("EvoNNEEEWWW-ToF-15-03-24--16-44.csv")

plt.figure(figsize = (10, 6))
plt.plot(file.timestamp, file.KF_altitutde_est)
plt.plot(file2.timestamp, file2.Altitude)

plt.title('Altitude')
plt.xlabel('Date_time')


plt.xticks([])
plt.ylabel('Altitude')
plt.grid(True)
plt.legend()

print(file)

plt.show()



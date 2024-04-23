import matplotlib.pyplot as plt 
import pandas as pd

filename = "Evo-ToF-22-04-24--13-46_NEW"
filename2 = "PressureSensor-22-04-24--13-46_NEW"
file = pd.read_csv(f"{filename}.csv")
file2 = pd.read_csv(f"{filename2}.csv")

# plt.figure(figsize = (10, 6))
plt.plot(file.timestamp, file.Altitude)
plt.plot(file2.timestamp, file2.Altitude)

plt.title('Altitude')
plt.xlabel('Time/s')
plt.ylabel('Altitude/m')
plt.grid(True)
plt.legend()

plt.savefig("altitude_test.png")


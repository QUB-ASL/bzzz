import matplotlib.pyplot as plt 
import pandas as pd

file = pd.read_csv("Anemometer-15-03-24--16-44.csv")
file2 = pd.read_csv("EvoNNEEEWWW-ToF-15-03-24--16-44.csv")

plt.figure(figsize = (10, 6))
plt.plot(file.Date_Time, file.H_direction)
# plt.plot(file2.timestamp, file2.Altitude)

plt.title('Altitude')
#plt.xlabel('Date_time')


plt.xticks([])
plt.ylabel('Altitude')
plt.grid(True)
plt.legend()

print(file)

plt.show()



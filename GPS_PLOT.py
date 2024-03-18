import matplotlib.pyplot as plt 
import pandas as pd

file = pd.read_csv("GNSS-15-03-24--16-44.csv")

plt.figure(figsize = (10, 6))
#plt.plot(file.Date_Time, file.Altitude)
#plt.plot(file.Date_Time, file.Latitude)
#plt.plot(file.Date_Time, file.Longitude)
plt.plot(file.Latitude, file.Longitude)

plt.title('Altitude')
#plt.xlabel('Date_time')


plt.xticks([])
plt.ylabel('Altitude')
plt.grid(True)
plt.legend()

print(file)

plt.show()



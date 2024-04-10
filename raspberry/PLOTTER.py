import matplotlib.pyplot as plt 
import pandas as pd

filename = "BB-09-04-24--18-50"

file = pd.read_csv(f"raspberry/{filename}.csv")

plt.figure(figsize = (10, 6))
plt.plot(file.datetime, file.z)
plt.plot(file.datetime, file.z_ref)
plt.plot(file.datetime, file.z_hat)
plt.plot(file.datetime, file.tau)

plt.plot(file.datetime, file.v_hat)

plt.title('Altitude')
#plt.xlabel('Date_time')


plt.xticks([])
plt.ylabel('Altitude')
plt.grid(True)
plt.legend()

plt.savefig(f"raspberry/{filename}.png")
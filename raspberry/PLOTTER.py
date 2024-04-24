import matplotlib.pyplot as plt 
import pandas as pd

filename = "BB-24-04-24--12-15"
file = pd.read_csv(f"{filename}.csv")

plt.figure(figsize = (10, 6))
plt.plot(file.datetime, file.z_tof)
plt.plot(file.datetime, file.z_ref)
plt.plot(file.datetime, file.z_hat)
plt.plot(file.datetime, file.z_hat_2)
plt.plot(file.datetime, file.tau)

plt.plot(file.datetime, file.v_hat)

plt.title('Altitude')
#plt.xlabel('Date_time')


plt.xticks([])
plt.ylabel('Altitude')
plt.grid(True)
plt.legend()

plt.savefig(f"{filename}.png")



# plt.figure(figsize = (10, 6))
# plt.plot(file.datetime, file.alpha_1)
# plt.plot(file.datetime, file.alpha_0)

# plt.title('Alphas')
# #plt.xlabel('Date_time')


# plt.xticks([])
# plt.grid(True)
# plt.legend()

# plt.savefig(f"{filename}_2.png")
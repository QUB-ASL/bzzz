import matplotlib.pyplot as plt 
import pandas as pd

file = pd.read_csv("raspberry/data/GNSS-16-04-25--12-11.csv")

# find the average latitude and longitude between the given number lines of csv file
line_numbers = [196, 772, 872, 1051]

distance_travelled = 0
plot_latitude_model = []
plot_longitude_model = []
plot_latitude_new_model = []
plot_longitude_new_model = []
distance_of_last_model = 0
for i in range(1,1055):
    
    distance_travelled = distance_travelled + ((file.N[i] - file.N[i-1])**2 + (file.E[i] - file.E[i-1])**2)**0.5

    if distance_travelled > 12.5:
        distance_of_last_model = distance_travelled
        distance_travelled = 0
        plot_latitude_model.append(file.N[i])
        plot_longitude_model.append(file.E[i])
        # print("New model at index: ", i)
    
    elif i == 196 or i == 772 or i == 872 or i == 1051:
        distance_travelled = 0

for i in range(len(line_numbers)):
    plot_latitude_new_model.append(file.N[line_numbers[i]])
    plot_longitude_new_model.append(file.E[line_numbers[i]])
#     if i == 0:
#         plot_latitude_model.append(file.N[0:line_numbers[i]].mean())
#         plot_longitude_model.append(file.E[0:line_numbers[i]].mean())
#     else:
#         plot_latitude_model.append(file.N[line_numbers[i-1]:line_numbers[i]].mean())
#         plot_longitude_model.append(file.E[line_numbers[i-1]:line_numbers[i]].mean())

# print(plot_latitude_model)
# print(plot_longitude_model)
# print(plot_latitude_new_model)
# print(plot_longitude_new_model)


plt.figure(figsize = (7, 4), dpi = 600)
plt.plot(file.N[0:line_numbers[3]], file.E[0:line_numbers[3]], label='Trajectory', linewidth=2)
plt.plot(file.N[line_numbers[3]:], file.E[line_numbers[3]:], linestyle=(0, (4, 8)), linewidth=2, c='tab:blue')
plt.plot(file.N[0], file.E[0], 'ro', markersize=8, c='purple', label='Start point')
plt.plot(-1.7, 0 , 'ro', markersize=8, c='tab:orange', label='New location')
plt.plot(plot_latitude_model, plot_longitude_model, 'ro', markersize=8, c='green', label=r'New model ($L_{\rm max}$)')
plt.plot(plot_latitude_new_model, plot_longitude_new_model, 'ro', markersize=8, c='red', label=r'New model($\epsilon_\theta$)')
# for i, (lat, lon) in enumerate(zip(plot_latitude_model, plot_longitude_model)):
#     plt.text(lat + 0.5, lon + 0.5, f"Model {i+1}", fontsize=18, ha='left', va='bottom')
plt.text(plot_latitude_model[3] + 0.5, plot_longitude_model[3] + 0.5, f"Model A", fontsize=14, ha='left', va='bottom')
plt.text(plot_latitude_model[7] - 0.5, plot_longitude_model[7] + 0.5, f"Model B", fontsize=14, ha='right', va='bottom')
plt.text(plot_latitude_model[10] - 0.5, plot_longitude_model[10] - 0.5, f"Model C", fontsize=14, ha='right', va='top')
plt.text(plot_latitude_new_model[-1] - 0.5, plot_longitude_new_model[-1] - 0.5, f"Model D", fontsize=14, ha='right', va='top')
plt.grid(True)
plt.legend(loc= (0.681, 0.648), fontsize=10)
plt.xlabel(r'North ($m$)', fontsize=14)
plt.ylabel(r'East ($m$)', fontsize=14)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.title('Model locations', fontsize=16)
plt.xlim(-40, 40)
plt.ylim(-40, 40)

plt.savefig('raspberry/data/Trajectory.pdf', dpi=600, bbox_inches='tight')


# plt.show()
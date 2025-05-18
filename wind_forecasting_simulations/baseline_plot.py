import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def plot_persistence_method(file_name,
                            prediction_horizon_1,):
    sample_time = 0.025
    time_ph_1 = prediction_horizon_1 * sample_time
#     time_ph_2 = prediction_horizon_2 * sample_time
    t_minus_ph_1 = pd.Series()
#     t_minus_ph_2 = pd.Series()
    error_ph_1 = pd.Series()
#     error_ph_2 = pd.Series()
    new_error = pd.Series()

    #read data
    df_wind = pd.read_csv(file_name)
    
    #set index
    df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="25ms")

    # prevous_error = 0

    for x in range(len(df_wind)-prediction_horizon_1):
            temp_pred = df_wind.V_axis.iloc[x]
            # temp_pred = temp_pred + 0.1*prevous_error
            t_minus_ph_1[df_wind.index[x+prediction_horizon_1]] = temp_pred
            error_ph_1[df_wind.index[x]] = np.sqrt((df_wind.V_axis.iloc[x + prediction_horizon_1] - t_minus_ph_1.iloc[x])**2)
            new_error[df_wind.index[x]] = abs(df_wind.V_axis.iloc[x + prediction_horizon_1] - t_minus_ph_1.iloc[x])
            # if x > prediction_horizon_1:
            #     prevous_error = df_wind.V_axis.iloc[x] - t_minus_ph_1.iloc[x-prediction_horizon_1]

    
#     for x in range(len(df_wind)-prediction_horizon_2):
#             t_minus_ph_2[df_wind.index[x+prediction_horizon_2]] = df_wind.V_axis[x]
#             error_ph_2[df_wind.index[x]] = np.sqrt((df_wind.V_axis[x+prediction_horizon_2] - t_minus_ph_2[x])**2)
    print(file_name)

    #save error to csv
    error_ph_1.to_csv(f'{file_name.split(".")[0]}_error_ph_1.csv', index=False)

    RMSE_ph_1 = np.sqrt(np.mean((df_wind.V_axis - t_minus_ph_1)**2))
    print(f'RMSE for t minus {prediction_horizon_1} is {RMSE_ph_1}')
#     RMSE_ph_2 = np.sqrt(np.mean((df_wind.V_axis - t_minus_ph_2)**2))
#     print(f'RMSE for t minus {prediction_horizon_2} is {RMSE_ph_2}')

    quantile_error_ph_1 = np.quantile(error_ph_1, 0.95)
    print(f'Quantile Error: {quantile_error_ph_1}')
    percentile_error = np.percentile(new_error, 95)
    print(f'Percentile Error: {percentile_error}')
#     quantile_error_ph_2 = np.quantile(error_ph_2, 0.95)
#     print(f'Quantile Error: {quantile_error_ph_2}')


    plt.figure(figsize=(10,4))
    plt.plot(df_wind.V_axis, label='wind speed', color='blue', linewidth=2)
    plt.plot(t_minus_ph_1, label=f'Persistence prediction using t minus {prediction_horizon_1}-steps ({time_ph_1} seconds)', color='red', linestyle='--', linewidth=2)
#     plt.plot(t_minus_ph_2, label=f'Persistence prediction using t minus {prediction_horizon_2}-steps ({time_ph_2} seconds)', color='red')
    plt.title('Persistence prediction of wind speed over time', fontsize=32)
    plt.legend(fontsize=20)
    plt.ylabel('Wind Speed (m/s)', fontsize=23)
    plt.xlabel('Time', fontsize=23)

    plt.figure(figsize=(10,4))
    sns.displot(error_ph_1, kind="kde", color='blue')
    sns.displot(new_error, kind="kde", color='green')
#     sns.distplot(error_ph_2, hist=False, color='red')
    plt.plot([RMSE_ph_1, RMSE_ph_1], [0, 1], color='darkblue')
#     plt.plot([RMSE_ph_2, RMSE_ph_2], [0, 1], color='firebrick')
    plt.text(RMSE_ph_1, 0.5, f'RMSE: {RMSE_ph_1:.2f}', color='darkblue', fontsize=20, ha='center')
#     plt.text(RMSE_ph_2, 0.5, f'RMSE: {RMSE_ph_2:.2f}', color='firebrick', fontsize=12, ha='center')
    plt.plot([quantile_error_ph_1, quantile_error_ph_1], [0, 1], color='darkblue')
#     plt.plot([quantile_error_ph_2, quantile_error_ph_2], [0, 1], color='firebrick')
    plt.plot([percentile_error, percentile_error], [0, 1], color='green')
    plt.text(quantile_error_ph_1, 0.5, f'95% Quantile \n Error: {quantile_error_ph_1:.2f}', color='darkblue', fontsize=20, ha='center')
#     plt.text(quantile_error_ph_2, 0.5, f'95% Quantile \n Error: {quantile_error_ph_2:.2f}', color='firebrick', fontsize=12, ha='center')
    plt.title(f'Probability Density Error of the Persistence predictions', fontsize=20)
    plt.legend((f'Error of Persistence prediction using t minus {prediction_horizon_1}-steps ({time_ph_1} seconds)'), fontsize=12)
    plt.ylabel('Probability Density', fontsize=16)
    plt.xlabel('Error (m/s)', fontsize=16)
    
    plt.show()

def assume_average_wind_speed(file_name):
    average_wind_speed = pd.Series()
    how_long = 10

    #read data
    df_wind = pd.read_csv(file_name)

    #set index
    df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="25L")

    average_wind = df_wind.V_axis[:how_long].mean()

    for x in range(len(df_wind)):
            if (x + 1) % how_long == 0:
                  average_wind = df_wind.V_axis[x-how_long+1:x+1].mean()
            average_wind_speed[df_wind.index[x]] = average_wind


    error = np.sqrt((df_wind.V_axis - average_wind_speed)**2)
    RMSE = np.sqrt(np.mean((df_wind.V_axis - average_wind_speed)**2))
    quantile_error = np.quantile(error, 0.95)

    plt.figure(figsize=(10,4))
    plt.plot(df_wind.V_axis, label='wind speed', color='black')
    plt.plot(average_wind_speed, label=f'Average wind speed', color='blue')
    plt.title('Average wind speed over time', fontsize=32)
    plt.legend(fontsize=20)
    plt.ylabel('Wind Speed (m/s)', fontsize=23)
    plt.xlabel('Time', fontsize=23)

    plt.figure(figsize=(10,4))
    sns.distplot(error, hist=False, color='blue')
    plt.plot([RMSE, RMSE], [0, 1], color='darkblue')
    plt.text(RMSE, 0.5, f'RMSE: {RMSE:.2f}', color='darkblue', fontsize=12, ha='center')
    plt.plot([quantile_error, quantile_error], [0, 1], color='darkblue')
    plt.text(quantile_error, 0.5, f'95% Quantile \n Error: {quantile_error:.2f}', color='darkblue', fontsize=12, ha='center')
    plt.title(f'Probability Density Error of the Average wind speed', fontsize=32)
    plt.legend(('Error of Average wind speed'), fontsize=20)
    plt.ylabel('Probability Density', fontsize=23)
    plt.xlabel('Error (m/s)', fontsize=23)
    
    plt.show()



# plot_persistence_method('raspberry/data/wind_data/25-09-23--17-06/25-09-23--17-06_N_10.csv', 10)
plot_persistence_method('raspberry/data/Anemometer-16-04-25--11-51_N_10.csv', 10)
# plot_persistence_method('raspberry/data/wind_data/december_2023/21-12-23--15-30/21-12-23--15-30_N_10.csv', 10)
# plot_persistence_method('raspberry/data/wind_data/december_2023/21-12-23--16-24/21-12-23--16-24_N_10.csv', 10)
# plot_persistence_method('raspberry/data/wind_data/december_2023/21-12-23--17-24/21-12-23--17-24_N_10.csv', 10)
# plot_persistence_method('raspberry/data/wind_data/december_2023/21-12-23--18-24/21-12-23--18-24_N_10.csv', 10)
# plot_persistence_method('raspberry/data/wind_data/december_2023/21-12-23--19-04/21-12-23--19-04_N_10.csv', 10)
# plot_persistence_method('raspberry/data/wind_data/december_2023/21-12-23--19-14/21-12-23--19-14_N_10.csv', 10)

# assume_average_wind_speed('raspberry/data/wind_data/25-09-23--16-49/25-09-23--16-49_N_10.csv')
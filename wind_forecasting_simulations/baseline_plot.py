import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def plot_persistence_method(file_name,
                            prediction_horizon):
    t_minus_x = pd.Series()
    error_i_V = pd.Series()

    #read data
    df_wind = pd.read_csv(file_name)
    
    #set index
    df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="25L")

    for x in range(len(df_wind)-prediction_horizon):
            t_minus_x[df_wind.index[x+prediction_horizon]] = df_wind.V_axis[x]
            error_i_V[df_wind.index[x]] = np.sqrt((df_wind.V_axis[x+prediction_horizon] - t_minus_x[x])**2)

    RMSE = np.sqrt(np.mean((df_wind.V_axis - t_minus_x)**2))
    print(f'RMSE for t minus {prediction_horizon} is {RMSE}')

    quantile_error_V = np.quantile(error_i_V, 0.95)

    print(f'Quantile Error: {quantile_error_V}')

    plt.figure(figsize=(10,4))
    plt.plot(df_wind.V_axis, label='wind speed')
    plt.plot(t_minus_x, label=f'Persistence prediction using t minus {prediction_horizon}')
    plt.title('Wind speed over Time', fontsize=20)
    plt.legend(fontsize=12)
    plt.ylabel('Wind Speed', fontsize=16)

    plt.figure(figsize=(10,4))
    sns.distplot(error_i_V, hist=False)
    plt.plot([RMSE, RMSE], [0, 1], color='Red')
    plt.text(RMSE, 0.5, f'RMSE: {RMSE:.2f}', color='Red', fontsize=12, ha='center')
    plt.plot([quantile_error_V, quantile_error_V], [0, 1], color='Green')
    plt.text(quantile_error_V, 0.5, f'Quantile Error: {quantile_error_V:.2f}', color='Green', fontsize=12, ha='center')
    plt.title(f'Probability Density Error of the Persistence prediction using t minus {prediction_horizon}', fontsize=20)
    plt.legend(('Error', 'RMSE', 'Quantile Error'), fontsize=12)
    plt.ylabel('Probability Density', fontsize=16)
    plt.xlabel('Error (m/s)', fontsize=16)
    
    plt.show()

plot_persistence_method('raspberry/data/wind_data/25-09-23--16-49/25-09-23--16-49_N_10.csv', 10)
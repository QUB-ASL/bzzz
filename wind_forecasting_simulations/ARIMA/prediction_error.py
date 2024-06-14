import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from statsmodels.tsa.stattools import adfuller
from pandas.plotting import register_matplotlib_converters
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.arima.model import ARIMA
register_matplotlib_converters()
from time import time
import matplotlib.dates as mdates
import seaborn as sns
import csv

def validate_model(file_name,
                   train_start,
                   train_end,
                   test_end,
                   ARIMA_p,
                   ARIMA_d,
                   ARIMA_q,
                   Prediction_horizon,
                   quantile_level,
                   logger: bool):
    
    if logger is True and ARIMA_p==0 and ARIMA_q==0:
        with open(f'{file_name}_quantile_error_U_{train_start}.csv', "w", newline="") as f:
            # creating the writer
            writer = csv.writer(f)
            # using writerow to write individual record one by one
            writer.writerow(["ARIMA Model", "Error Index"])
        
        with open(f'{file_name}_quantile_error_V_{train_start}.csv', "w", newline="") as f:
            # creating the writer
            writer = csv.writer(f)
            # using writerow to write individual record one by one
            writer.writerow(["ARIMA Model", "Error Index"])
        
        with open(f'{file_name}_quantile_error_W_{train_start}.csv', "w", newline="") as f:
            # creating the writer
            writer = csv.writer(f)
            # using writerow to write individual record one by one
            writer.writerow(["ARIMA Model", "Error Index"])
    
    #read data
    df_wind = pd.read_csv(f'{file_name}.csv')
    
    #set index
    df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="25L")
    
    #split data set
    train_data_U = df_wind.U_axis[train_start:train_end]
    test_data_U = df_wind.U_axis[(train_end):test_end]
    train_data_V = df_wind.V_axis[train_start:train_end]
    test_data_V = df_wind.V_axis[(train_end):test_end]
    train_data_W = df_wind.W_axis[train_start:train_end]
    test_data_W = df_wind.W_axis[(train_end):test_end]
    
    # define model
    model_U = ARIMA(train_data_U, order=(ARIMA_p, ARIMA_d, ARIMA_q))
    model_V = ARIMA(train_data_V, order=(ARIMA_p, ARIMA_d, ARIMA_q))
    model_W = ARIMA(train_data_W, order=(ARIMA_p, ARIMA_d, ARIMA_q))
    
    #fit the model
    model_fit_U = model_U.fit()
    model_fit_V = model_V.fit()
    model_fit_W = model_W.fit()
    
    rolling_predictions_U = {}
    rolling_predictions_V = {}
    rolling_predictions_W = {}
    error_i_U = pd.Series()
    error_i_V = pd.Series()
    error_i_W = pd.Series()
    for x in range(train_end, test_end):
        updated_data_U = df_wind.U_axis[x:x+1]
        updated_data_V = df_wind.V_axis[x:x+1]
        updated_data_W = df_wind.W_axis[x:x+1]
        model_fit_U = model_fit_U.append(updated_data_U, refit=False)
        model_fit_V = model_fit_V.append(updated_data_V, refit=False)
        model_fit_W = model_fit_W.append(updated_data_W, refit=False)
    
        rolling_predictions_U[x+1] = model_fit_U.predict(start=(x+1),end=(x+Prediction_horizon))
        rolling_predictions_V[x+1] = model_fit_V.predict(start=(x+1),end=(x+Prediction_horizon))
        rolling_predictions_W[x+1] = model_fit_W.predict(start=(x+1),end=(x+Prediction_horizon))

        error_i_U[df_wind.index[x]] = np.sqrt(sum((df_wind.U_axis[x+1:x+Prediction_horizon+1] 
                                                   - rolling_predictions_U[x+1])**2)/Prediction_horizon)
        error_i_V[df_wind.index[x]] = np.sqrt(sum((df_wind.V_axis[x+1:x+Prediction_horizon+1] 
                                                   - rolling_predictions_V[x+1])**2)/Prediction_horizon)
        error_i_W[df_wind.index[x]] = np.sqrt(sum((df_wind.W_axis[x+1:x+Prediction_horizon+1] 
                                                   - rolling_predictions_W[x+1])**2)/Prediction_horizon)
    
    
    quantile_error_U = np.quantile(error_i_U, quantile_level)
    quantile_error_W = np.quantile(error_i_V, quantile_level)
    quantile_error_V = np.quantile(error_i_W, quantile_level)

    print(f'Error Index of ARMA({str(ARIMA_p)},0,{str(ARIMA_q)})')
    print(f'U_axis = {str(quantile_error_U)}')
    print(f'V_axis = {str(quantile_error_V)}')
    print(f'W_axis = {str(quantile_error_W)}')
    
    if logger is True:
        with open(f'{file_name}_quantile_error_U_{train_start}.csv', "a+", newline="") as f:
                    # creating the writer
                    writer = csv.writer(f)
                    # using writerow to write individual record one by one
                    writer.writerow([f'({str(ARIMA_p)},0,{str(ARIMA_q)})', quantile_error_U])

        with open(f'{file_name}_quantile_error_V_{train_start}.csv', "a+", newline="") as f:
                    # creating the writer
                    writer = csv.writer(f)
                    # using writerow to write individual record one by one
                    writer.writerow([f'({str(ARIMA_p)},0,{str(ARIMA_q)})', quantile_error_V])

        with open(f'{file_name}_quantile_error_W_{train_start}.csv', "a+", newline="") as f:
                    # creating the writer
                    writer = csv.writer(f)
                    # using writerow to write individual record one by one
                    writer.writerow([f'({str(ARIMA_p)},0,{str(ARIMA_q)})', quantile_error_W])

    # if quantile_error_U < 1.29 :
    #   plt.figure(figsize=(10,4))
    #   sns.distplot(error_i_U, hist=False)
    #   plt.plot([quantile_error_U, quantile_error_U], [0, 1], color='C0')
    #   plt.title(f'Error Index of ARIMA({str(ARIMA_p)},0,{str(ARIMA_q)})', fontsize=20)
    #   plt.ylabel('Density', fontsize=16)
    #   plt.xlabel('Error value', fontsize=16)
                       
    return 0

# for i in range(10):
#     for j in range(10):
#         validate_model('raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_5',4000,8000,8500,i,0,j,10,0.95)

validate_model('raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_5',0,2000,2005,2,0,2,10,0.95,False)

plt.show()
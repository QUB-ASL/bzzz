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
import csv

def fit_and_forecast(file_name,
                     train_end,
                     test_end,
                     prediction_horizon,
                     ARIMA_p_1,
                     ARIMA_d_1,
                     ARIMA_q_1,
                     ARIMA_p_2 = None,
                     ARIMA_d_2 = None,
                     ARIMA_q_2 = None,
                     wind_velocity_at_T_minus_prediction_horizon: bool = False,
                     combined_wind_speed: bool = False,
                     U: bool = False,
                     V: bool = False,
                     W: bool = False):
    
    ## Read data
    df_wind = pd.read_csv(file_name)
    
    ## Set index
    df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="25L")
    
    if combined_wind_speed is True:
        ## Plot Wind Speed against time
        plt.figure(figsize=(10,4))
        plt.plot(df_wind.Wind_Speed)
        plt.title('combined Wind speed over Time', fontsize=20)
        plt.ylabel('Wind Speed m/s', fontsize=16)
        
        ## Plot ACF and PACF
        plot_acf(df_wind.Wind_Speed, lags=50)
        plot_pacf(df_wind.Wind_Speed, lags=50)
        
        ## Split the data 
        train_data = df_wind.Wind_Speed[:train_end]
        test_data = df_wind.Wind_Speed[(train_end):test_end]
        
        ## Define and fit the model
        model_1 = ARIMA(train_data, order=(ARIMA_p_1, ARIMA_d_1, ARIMA_q_1))
        model_fit_1 = model_1.fit()

        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            model_2 = ARIMA(train_data, order=(ARIMA_p_2, ARIMA_d_2, ARIMA_q_2))
            model_fit_2 = model_2.fit()
        
        # ## Summary of the model
        print(f'model_fit_1 summary = {model_fit_1.summary()}')
        print(f'model_fit_1 params = {model_fit_1.params}')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            print(f'model_fit_2 summary = {model_fit_2.summary()}')
            print(f'model_fit_2 params = {model_fit_2.params}')
        
        start = time()
        ## Define series 
        rolling_predictions_1 = pd.Series()
        t_minus_x = pd.Series()
        rolling_predictions_2 = pd.Series()
        
        ## Rolling prediction for wind speed
        for x in range(train_end, test_end):
            t_minus_x[df_wind.index[x+prediction_horizon]] = df_wind.Wind_Speed[x]
            updated_data = df_wind.Wind_Speed[x:x+1]
            model_fit_1 = model_fit_1.append(updated_data, refit=False)
            rolling_predictions_1[df_wind.index[x+prediction_horizon]] = model_fit_1.predict(x+prediction_horizon)

            if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                model_fit_2 = model_fit_2.append(updated_data, refit=False)
                rolling_predictions_2[df_wind.index[x+prediction_horizon]] = model_fit_2.predict(x+prediction_horizon)
            
            # with open('rolling_predictions.csv', "a+", newline="") as f:
            #     # creating the writer
            #     writer = csv.writer(f)
            #     # using writerow to write individual record one by one
            #     writer.writerow([rolling_predictions_1[df_wind.index[x+prediction_horizon_1]]])
        
        end = time()
        print('Model Fitting Time:', end - start)
        
        ## Get residuals for rolling prediction and using previous wind speed
        residuals_rolling_predictions_1 = test_data - rolling_predictions_1
        residuals_t_minus_x = test_data - t_minus_x
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                residuals_rolling_predictions_2 = test_data - rolling_predictions_2
    
        
        ## Plot rolling predictions and test data against time
        plt.figure(figsize=(10,4))
        plt.plot(test_data, label='Data')
        plt.plot(rolling_predictions_1, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(rolling_predictions_2, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(t_minus_x, label=f't_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('Rolling Wind Prediction', fontsize=20)
        plt.ylabel('Wind Speed m/s', fontsize=16)
        
        ## Plot Residuals against time for rolling prediction
        plt.figure(figsize=(10,4))
        plt.plot(residuals_rolling_predictions_1, label = f'residuals for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(residuals_rolling_predictions_2, label = f'residuals for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(residuals_t_minus_x, label = f'residuals_t_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('Residuals from rolling Wind Prediction', fontsize=20)
        plt.ylabel('Error', fontsize=16)
        plt.axhline(0, color='r', linestyle='--', alpha=0.2)


    if U is True:
        ## Plot Wind Speed against time
        plt.figure(figsize=(10,4))
        plt.plot(df_wind.U_axis)
        plt.title('U Wind velocity over Time', fontsize=20)
        plt.ylabel('Wind velocity m/s', fontsize=16)
        
        ## Plot ACF and PACF
        plot_acf(df_wind.U_axis, lags=50)
        plot_pacf(df_wind.U_axis, lags=50)
        
        ## Split the data 
        train_data = df_wind.U_axis[:train_end]
        test_data = df_wind.U_axis[(train_end):test_end]
        
        ## Define and fit the model
        model_1 = ARIMA(train_data, order=(ARIMA_p_1, ARIMA_d_1, ARIMA_q_1))
        model_fit_1 = model_1.fit()

        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            model_2 = ARIMA(train_data, order=(ARIMA_p_2, ARIMA_d_2, ARIMA_q_2))
            model_fit_2 = model_2.fit()
        
        # ## Summary of the model
        print(f'model_fit_1 summary = {model_fit_1.summary()}')
        print(f'model_fit_1 params = {model_fit_1.params}')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            print(f'model_fit_2 summary = {model_fit_2.summary()}')
            print(f'model_fit_2 params = {model_fit_2.params}')
        
        start = time()
        ## Define series 
        rolling_predictions_1 = pd.Series()
        t_minus_x = pd.Series()
        rolling_predictions_2 = pd.Series()
        
        ## Rolling prediction for wind speed
        for x in range(train_end, test_end):
            t_minus_x[df_wind.index[x+prediction_horizon]] = df_wind.U_axis[x]
            updated_data = df_wind.U_axis[x:x+1]
            model_fit_1 = model_fit_1.append(updated_data, refit=False)
            rolling_predictions_1[df_wind.index[x+prediction_horizon]] = model_fit_1.predict(x+prediction_horizon)

            if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                model_fit_2 = model_fit_2.append(updated_data, refit=False)
                rolling_predictions_2[df_wind.index[x+prediction_horizon]] = model_fit_2.predict(x+prediction_horizon)
            
            # with open('rolling_predictions.csv', "a+", newline="") as f:
            #     # creating the writer
            #     writer = csv.writer(f)
            #     # using writerow to write individual record one by one
            #     writer.writerow([rolling_predictions_1[df_wind.index[x+prediction_horizon_1]]])
        
        end = time()
        print('Model Fitting Time:', end - start)
        
        ## Get residuals for rolling prediction and using previous wind speed
        residuals_rolling_predictions_1 = test_data - rolling_predictions_1
        residuals_t_minus_x = test_data - t_minus_x
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                residuals_rolling_predictions_2 = test_data - rolling_predictions_2
    
        
        ## Plot rolling predictions and test data against time
        plt.figure(figsize=(10,4))
        plt.plot(test_data, label='Data')
        plt.plot(rolling_predictions_1, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(rolling_predictions_2, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(t_minus_x, label=f't_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('U_axis Rolling Wind Prediction', fontsize=20)
        plt.ylabel('Wind Speed m/s', fontsize=16)
        
        ## Plot Residuals against time for rolling prediction
        plt.figure(figsize=(10,4))
        plt.plot(residuals_rolling_predictions_1, label = f'residuals for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(residuals_rolling_predictions_2, label = f'residuals for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(residuals_t_minus_x, label = f'residuals_t_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('Residuals from U_axis rolling Wind Prediction', fontsize=20)
        plt.ylabel('Error', fontsize=16)
        plt.axhline(0, color='r', linestyle='--', alpha=0.2)


    if V is True:
        ## Plot Wind Speed against time
        plt.figure(figsize=(10,4))
        plt.plot(df_wind.V_axis)
        plt.title('V Wind velocity over Time', fontsize=20)
        plt.ylabel('Wind velocity m/s', fontsize=16)
        
        ## Plot ACF and PACF
        plot_acf(df_wind.V_axis, lags=50)
        plot_pacf(df_wind.V_axis, lags=50)
        
        ## Split the data 
        train_data = df_wind.V_axis[:train_end]
        test_data = df_wind.V_axis[(train_end):test_end]
        
        ## Define and fit the model
        model_1 = ARIMA(train_data, order=(ARIMA_p_1, ARIMA_d_1, ARIMA_q_1))
        model_fit_1 = model_1.fit()

        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            model_2 = ARIMA(train_data, order=(ARIMA_p_2, ARIMA_d_2, ARIMA_q_2))
            model_fit_2 = model_2.fit()
        
        # ## Summary of the model
        print(f'model_fit_1 summary = {model_fit_1.summary()}')
        print(f'model_fit_1 params = {model_fit_1.params}')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            print(f'model_fit_2 summary = {model_fit_2.summary()}')
            print(f'model_fit_2 params = {model_fit_2.params}')
        
        start = time()
        ## Define series 
        rolling_predictions_1 = pd.Series()
        t_minus_x = pd.Series()
        rolling_predictions_2 = pd.Series()
        
        ## Rolling prediction for wind speed
        for x in range(train_end, test_end):
            t_minus_x[df_wind.index[x+prediction_horizon]] = df_wind.V_axis[x]
            updated_data = df_wind.V_axis[x:x+1]
            model_fit_1 = model_fit_1.append(updated_data, refit=False)
            rolling_predictions_1[df_wind.index[x+prediction_horizon]] = model_fit_1.predict(x+prediction_horizon)

            if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                model_fit_2 = model_fit_2.append(updated_data, refit=False)
                rolling_predictions_2[df_wind.index[x+prediction_horizon]] = model_fit_2.predict(x+prediction_horizon)
            
            # with open('rolling_predictions.csv', "a+", newline="") as f:
            #     # creating the writer
            #     writer = csv.writer(f)
            #     # using writerow to write individual record one by one
            #     writer.writerow([rolling_predictions_1[df_wind.index[x+prediction_horizon_1]]])
        
        end = time()
        print('Model Fitting Time:', end - start)
        
        ## Get residuals for rolling prediction and using previous wind speed
        residuals_rolling_predictions_1 = test_data - rolling_predictions_1
        residuals_t_minus_x = test_data - t_minus_x
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                residuals_rolling_predictions_2 = test_data - rolling_predictions_2
    
        
        ## Plot rolling predictions and test data against time
        plt.figure(figsize=(10,4))
        plt.plot(test_data, label='Data')
        plt.plot(rolling_predictions_1, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(rolling_predictions_2, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(t_minus_x, label=f't_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('V_axis Rolling Wind Prediction', fontsize=20)
        plt.ylabel('Wind Speed m/s', fontsize=16)
        
        ## Plot Residuals against time for rolling prediction
        plt.figure(figsize=(10,4))
        plt.plot(residuals_rolling_predictions_1, label = f'residuals for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(residuals_rolling_predictions_2, label = f'residuals for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(residuals_t_minus_x, label = f'residuals_t_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('Residuals from V_axis rolling Wind Prediction', fontsize=20)
        plt.ylabel('Error', fontsize=16)
        plt.axhline(0, color='r', linestyle='--', alpha=0.2)


    if W is True:
        ## Plot Wind Speed against time
        plt.figure(figsize=(10,4))
        plt.plot(df_wind.W_axis)
        plt.title('W Wind velocity over Time', fontsize=20)
        plt.ylabel('Wind velocity m/s', fontsize=16)
        
        ## Plot ACF and PACF
        plot_acf(df_wind.W_axis, lags=50)
        plot_pacf(df_wind.W_axis, lags=50)
        
        ## Split the data 
        train_data = df_wind.W_axis[:train_end]
        test_data = df_wind.W_axis[(train_end):test_end]
        
        ## Define and fit the model
        model_1 = ARIMA(train_data, order=(ARIMA_p_1, ARIMA_d_1, ARIMA_q_1))
        model_fit_1 = model_1.fit()

        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            model_2 = ARIMA(train_data, order=(ARIMA_p_2, ARIMA_d_2, ARIMA_q_2))
            model_fit_2 = model_2.fit()
        
        # ## Summary of the model
        print(f'model_fit_1 summary = {model_fit_1.summary()}')
        print(f'model_fit_1 params = {model_fit_1.params}')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            print(f'model_fit_2 summary = {model_fit_2.summary()}')
            print(f'model_fit_2 params = {model_fit_2.params}')
        
        start = time()
        ## Define series 
        rolling_predictions_1 = pd.Series()
        t_minus_x = pd.Series()
        rolling_predictions_2 = pd.Series()
        
        ## Rolling prediction for wind speed
        for x in range(train_end, test_end):
            t_minus_x[df_wind.index[x+prediction_horizon]] = df_wind.W_axis[x]
            updated_data = df_wind.W_axis[x:x+1]
            model_fit_1 = model_fit_1.append(updated_data, refit=False)
            rolling_predictions_1[df_wind.index[x+prediction_horizon]] = model_fit_1.predict(x+prediction_horizon)

            if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                model_fit_2 = model_fit_2.append(updated_data, refit=False)
                rolling_predictions_2[df_wind.index[x+prediction_horizon]] = model_fit_2.predict(x+prediction_horizon)
            
            # with open('rolling_predictions.csv', "a+", newline="") as f:
            #     # creating the writer
            #     writer = csv.writer(f)
            #     # using writerow to write individual record one by one
            #     writer.writerow([rolling_predictions_1[df_wind.index[x+prediction_horizon_1]]])
        
        end = time()
        print('Model Fitting Time:', end - start)
        
        ## Get residuals for rolling prediction and using previous wind speed
        residuals_rolling_predictions_1 = test_data - rolling_predictions_1
        residuals_t_minus_x = test_data - t_minus_x
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                residuals_rolling_predictions_2 = test_data - rolling_predictions_2
    
        
        ## Plot rolling predictions and test data against time
        plt.figure(figsize=(10,4))
        plt.plot(test_data, label='Data')
        plt.plot(rolling_predictions_1, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(rolling_predictions_2, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(t_minus_x, label=f't_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('W_axis Rolling Wind Prediction', fontsize=20)
        plt.ylabel('Wind Speed m/s', fontsize=16)
        
        ## Plot Residuals against time for rolling prediction
        plt.figure(figsize=(10,4))
        plt.plot(residuals_rolling_predictions_1, label = f'residuals for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(residuals_rolling_predictions_2, label = f'residuals for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(residuals_t_minus_x, label = f'residuals_t_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('Residuals from W_axis rolling Wind Prediction', fontsize=20)
        plt.ylabel('Error', fontsize=16)
        plt.axhline(0, color='r', linestyle='--', alpha=0.2)


def fix_params_and_forecast(file_name,
                            train_end,
                            test_end,
                            prediction_horizon,
                            ARIMA_p_1,
                            ARIMA_d_1,
                            ARIMA_q_1,
                            fix_params_1 = None,
                            ARIMA_p_2 = None,
                            ARIMA_d_2 = None,
                            ARIMA_q_2 = None,
                            fix_params_2 = None,
                            wind_velocity_at_T_minus_prediction_horizon: bool = False,
                            combined_wind_speed: bool = False,
                            U: bool = False,
                            V: bool = False,
                            W: bool = False):
    
    ## Read data
    df_wind = pd.read_csv(file_name)
    
    ## Set index
    df_wind.index = pd.date_range(df_wind.Index_2[0], df_wind.Index_2.iloc[-1], freq="25L")

    if combined_wind_speed is True:
        ## Plot Wind Speed against time
        plt.figure(figsize=(10,4))
        plt.plot(df_wind.Wind_Speed)
        plt.title('combined Wind speed over Time', fontsize=20)
        plt.ylabel('Wind Speed m/s', fontsize=16)
        
        ## Plot ACF and PACF
        plot_acf(df_wind.Wind_Speed, lags=50)
        plot_pacf(df_wind.Wind_Speed, lags=50)
        
        ## Split the data 
        train_data = df_wind.Wind_Speed[:train_end]
        test_data = df_wind.Wind_Speed[(train_end):test_end]
        
        ## Define and fit the model
        model_1 = ARIMA(train_data, order=(ARIMA_p_1, ARIMA_d_1, ARIMA_q_1))
        with model_1.fix_params(fix_params_1):
            model_fit_1 = model_1.fit()

        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            model_2 = ARIMA(test_data, order=(ARIMA_p_2, ARIMA_d_2, ARIMA_q_2))
            with model_2.fix_params(fix_params_2):
                model_fit_2 = model_2.fit()
        
        # ## Summary of the model
        print(f'model_fit_1 summary = {model_fit_1.summary()}')
        print(f'model_fit_1 params = {model_fit_1.params}')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            print(f'model_fit_2 summary = {model_fit_2.summary()}')
            print(f'model_fit_2 params = {model_fit_2.params}')
        
        start = time()
        ## Define series 
        rolling_predictions_1 = pd.Series()
        t_minus_x = pd.Series()
        rolling_predictions_2 = pd.Series()
        
        ## Rolling prediction for wind speed
        for x in range(train_end, test_end):
            t_minus_x[df_wind.index[x+prediction_horizon]] = df_wind.Wind_Speed[x]
            updated_data = df_wind.Wind_Speed[x:x+1]
            model_fit_1 = model_fit_1.append(updated_data, refit=False)
            rolling_predictions_1[df_wind.index[x+prediction_horizon]] = model_fit_1.predict(x+prediction_horizon)

            if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                model_fit_2 = model_fit_2.append(updated_data, refit=False)
                rolling_predictions_2[df_wind.index[x+prediction_horizon]] = model_fit_2.predict(x+prediction_horizon)
            
            # with open('rolling_predictions.csv', "a+", newline="") as f:
            #     # creating the writer
            #     writer = csv.writer(f)
            #     # using writerow to write individual record one by one
            #     writer.writerow([rolling_predictions_1[df_wind.index[x+prediction_horizon_1]]])
        
        end = time()
        print('Model Fitting Time:', end - start)
        
        ## Get residuals for rolling prediction and using previous wind speed
        residuals_rolling_predictions_1 = test_data - rolling_predictions_1
        residuals_t_minus_x = test_data - t_minus_x
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                residuals_rolling_predictions_2 = test_data - rolling_predictions_2
    
        
        ## Plot rolling predictions and test data against time
        plt.figure(figsize=(10,4))
        plt.plot(test_data, label='Data')
        plt.plot(rolling_predictions_1, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(rolling_predictions_2, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(t_minus_x, label=f't_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('Rolling Wind Prediction', fontsize=20)
        plt.ylabel('Wind Speed m/s', fontsize=16)
        
        ## Plot Residuals against time for rolling prediction
        plt.figure(figsize=(10,4))
        plt.plot(residuals_rolling_predictions_1, label = f'residuals for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(residuals_rolling_predictions_2, label = f'residuals for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(residuals_t_minus_x, label = f'residuals_t_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('Residuals from rolling Wind Prediction', fontsize=20)
        plt.ylabel('Error', fontsize=16)
        plt.axhline(0, color='r', linestyle='--', alpha=0.2)


    if U is True:
        ## Plot Wind Speed against time
        plt.figure(figsize=(10,4))
        plt.plot(df_wind.U_axis)
        plt.title('U Wind velocity over Time', fontsize=20)
        plt.ylabel('Wind velocity m/s', fontsize=16)
        
        ## Plot ACF and PACF
        plot_acf(df_wind.U_axis, lags=50)
        plot_pacf(df_wind.U_axis, lags=50)
        
        ## Split the data 
        train_data = df_wind.U_axis[:train_end]
        test_data = df_wind.U_axis[(train_end):test_end]
        
        ## Define and fit the model
        model_1 = ARIMA(train_data, order=(ARIMA_p_1, ARIMA_d_1, ARIMA_q_1))
        with model_1.fix_params(fix_params_1):
            model_fit_1 = model_1.fit()

        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            model_2 = ARIMA(test_data, order=(ARIMA_p_2, ARIMA_d_2, ARIMA_q_2))
            with model_2.fix_params(fix_params_2):
                model_fit_2 = model_2.fit()
        
        # ## Summary of the model
        print(f'model_fit_1 summary = {model_fit_1.summary()}')
        print(f'model_fit_1 params = {model_fit_1.params}')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            print(f'model_fit_2 summary = {model_fit_2.summary()}')
            print(f'model_fit_2 params = {model_fit_2.params}')
        
        start = time()
        ## Define series 
        rolling_predictions_1 = pd.Series()
        t_minus_x = pd.Series()
        rolling_predictions_2 = pd.Series()
        
        ## Rolling prediction for wind speed
        for x in range(train_end, test_end):
            t_minus_x[df_wind.index[x+prediction_horizon]] = df_wind.U_axis[x]
            updated_data = df_wind.U_axis[x:x+1]
            model_fit_1 = model_fit_1.append(updated_data, refit=False)
            rolling_predictions_1[df_wind.index[x+prediction_horizon]] = model_fit_1.predict(x+prediction_horizon)

            if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                model_fit_2 = model_fit_2.append(updated_data, refit=False)
                rolling_predictions_2[df_wind.index[x+prediction_horizon]] = model_fit_2.predict(x+prediction_horizon)
            
            # with open('rolling_predictions.csv', "a+", newline="") as f:
            #     # creating the writer
            #     writer = csv.writer(f)
            #     # using writerow to write individual record one by one
            #     writer.writerow([rolling_predictions_1[df_wind.index[x+prediction_horizon_1]]])
        
        end = time()
        print('Model Fitting Time:', end - start)
        
        ## Get residuals for rolling prediction and using previous wind speed
        residuals_rolling_predictions_1 = test_data - rolling_predictions_1
        residuals_t_minus_x = test_data - t_minus_x
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                residuals_rolling_predictions_2 = test_data - rolling_predictions_2
    
        
        ## Plot rolling predictions and test data against time
        plt.figure(figsize=(10,4))
        plt.plot(test_data, label='Data')
        plt.plot(rolling_predictions_1, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(rolling_predictions_2, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(t_minus_x, label=f't_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('U_axis Rolling Wind Prediction', fontsize=20)
        plt.ylabel('Wind Speed m/s', fontsize=16)
        
        ## Plot Residuals against time for rolling prediction
        plt.figure(figsize=(10,4))
        plt.plot(residuals_rolling_predictions_1, label = f'residuals for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(residuals_rolling_predictions_2, label = f'residuals for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(residuals_t_minus_x, label = f'residuals_t_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('Residuals from U_axis rolling Wind Prediction', fontsize=20)
        plt.ylabel('Error', fontsize=16)
        plt.axhline(0, color='r', linestyle='--', alpha=0.2)


    if V is True:
        ## Plot Wind Speed against time
        plt.figure(figsize=(10,4))
        plt.plot(df_wind.V_axis)
        plt.title('V Wind velocity over Time', fontsize=20)
        plt.ylabel('Wind velocity m/s', fontsize=16)
        
        ## Plot ACF and PACF
        plot_acf(df_wind.V_axis, lags=50)
        plot_pacf(df_wind.V_axis, lags=50)
        
        ## Split the data 
        train_data = df_wind.V_axis[:train_end]
        test_data = df_wind.V_axis[(train_end):test_end]
        
        ## Define and fit the model
        model_1 = ARIMA(train_data, order=(ARIMA_p_1, ARIMA_d_1, ARIMA_q_1))
        with model_1.fix_params(fix_params_1):
            model_fit_1 = model_1.fit()

        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            model_2 = ARIMA(test_data, order=(ARIMA_p_2, ARIMA_d_2, ARIMA_q_2))
            with model_2.fix_params(fix_params_2):
                model_fit_2 = model_2.fit()
        
        # ## Summary of the model
        print(f'model_fit_1 summary = {model_fit_1.summary()}')
        print(f'model_fit_1 params = {model_fit_1.params}')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            print(f'model_fit_2 summary = {model_fit_2.summary()}')
            print(f'model_fit_2 params = {model_fit_2.params}')
        
        start = time()
        ## Define series 
        rolling_predictions_1 = pd.Series()
        t_minus_x = pd.Series()
        rolling_predictions_2 = pd.Series()
        
        ## Rolling prediction for wind speed
        for x in range(train_end, test_end):
            t_minus_x[df_wind.index[x+prediction_horizon]] = df_wind.V_axis[x]
            updated_data = df_wind.V_axis[x:x+1]
            model_fit_1 = model_fit_1.append(updated_data, refit=False)
            rolling_predictions_1[df_wind.index[x+prediction_horizon]] = model_fit_1.predict(x+prediction_horizon)

            if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                model_fit_2 = model_fit_2.append(updated_data, refit=False)
                rolling_predictions_2[df_wind.index[x+prediction_horizon]] = model_fit_2.predict(x+prediction_horizon)
            
            # with open('rolling_predictions.csv', "a+", newline="") as f:
            #     # creating the writer
            #     writer = csv.writer(f)
            #     # using writerow to write individual record one by one
            #     writer.writerow([rolling_predictions_1[df_wind.index[x+prediction_horizon_1]]])
        
        end = time()
        print('Model Fitting Time:', end - start)
        
        ## Get residuals for rolling prediction and using previous wind speed
        residuals_rolling_predictions_1 = test_data - rolling_predictions_1
        residuals_t_minus_x = test_data - t_minus_x
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                residuals_rolling_predictions_2 = test_data - rolling_predictions_2
    
        
        ## Plot rolling predictions and test data against time
        plt.figure(figsize=(10,4))
        plt.plot(test_data, label='Data')
        plt.plot(rolling_predictions_1, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(rolling_predictions_2, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(t_minus_x, label=f't_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('V_axis Rolling Wind Prediction', fontsize=20)
        plt.ylabel('Wind Speed m/s', fontsize=16)
        
        ## Plot Residuals against time for rolling prediction
        plt.figure(figsize=(10,4))
        plt.plot(residuals_rolling_predictions_1, label = f'residuals for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(residuals_rolling_predictions_2, label = f'residuals for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(residuals_t_minus_x, label = f'residuals_t_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('Residuals from V_axis rolling Wind Prediction', fontsize=20)
        plt.ylabel('Error', fontsize=16)
        plt.axhline(0, color='r', linestyle='--', alpha=0.2)


    if W is True:
        ## Plot Wind Speed against time
        plt.figure(figsize=(10,4))
        plt.plot(df_wind.W_axis)
        plt.title('W Wind velocity over Time', fontsize=20)
        plt.ylabel('Wind velocity m/s', fontsize=16)
        
        ## Plot ACF and PACF
        plot_acf(df_wind.W_axis, lags=50)
        plot_pacf(df_wind.W_axis, lags=50)
        
        ## Split the data 
        train_data = df_wind.W_axis[:train_end]
        test_data = df_wind.W_axis[(train_end):test_end]
        
        ## Define and fit the model
        model_1 = ARIMA(train_data, order=(ARIMA_p_1, ARIMA_d_1, ARIMA_q_1))
        with model_1.fix_params(fix_params_1):
            model_fit_1 = model_1.fit()

        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            model_2 = ARIMA(test_data, order=(ARIMA_p_2, ARIMA_d_2, ARIMA_q_2))
            with model_2.fix_params(fix_params_2):
                model_fit_2 = model_2.fit()
        
        # ## Summary of the model
        print(f'model_fit_1 summary = {model_fit_1.summary()}')
        print(f'model_fit_1 params = {model_fit_1.params}')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            print(f'model_fit_2 summary = {model_fit_2.summary()}')
            print(f'model_fit_2 params = {model_fit_2.params}')
        
        start = time()
        ## Define series 
        rolling_predictions_1 = pd.Series()
        t_minus_x = pd.Series()
        rolling_predictions_2 = pd.Series()
        
        ## Rolling prediction for wind speed
        for x in range(train_end, test_end):
            t_minus_x[df_wind.index[x+prediction_horizon]] = df_wind.W_axis[x]
            updated_data = df_wind.W_axis[x:x+1]
            model_fit_1 = model_fit_1.append(updated_data, refit=False)
            rolling_predictions_1[df_wind.index[x+prediction_horizon]] = model_fit_1.predict(x+prediction_horizon)

            if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                model_fit_2 = model_fit_2.append(updated_data, refit=False)
                rolling_predictions_2[df_wind.index[x+prediction_horizon]] = model_fit_2.predict(x+prediction_horizon)
            
            # with open('rolling_predictions.csv', "a+", newline="") as f:
            #     # creating the writer
            #     writer = csv.writer(f)
            #     # using writerow to write individual record one by one
            #     writer.writerow([rolling_predictions_1[df_wind.index[x+prediction_horizon_1]]])
        
        end = time()
        print('Model Fitting Time:', end - start)
        
        ## Get residuals for rolling prediction and using previous wind speed
        residuals_rolling_predictions_1 = test_data - rolling_predictions_1
        residuals_t_minus_x = test_data - t_minus_x
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
                residuals_rolling_predictions_2 = test_data - rolling_predictions_2
    
        
        ## Plot rolling predictions and test data against time
        plt.figure(figsize=(10,4))
        plt.plot(test_data, label='Data')
        plt.plot(rolling_predictions_1, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(rolling_predictions_2, label = f'{prediction_horizon} step Prediction for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(t_minus_x, label=f't_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('W_axis Rolling Wind Prediction', fontsize=20)
        plt.ylabel('Wind Speed m/s', fontsize=16)
        
        ## Plot Residuals against time for rolling prediction
        plt.figure(figsize=(10,4))
        plt.plot(residuals_rolling_predictions_1, label = f'residuals for ({str(ARIMA_p_1)},0,{str(ARIMA_q_1)})')
        if ARIMA_p_2 is not None and ARIMA_d_2 is not None and ARIMA_q_2 is not None:
            plt.plot(residuals_rolling_predictions_2, label = f'residuals for ({str(ARIMA_p_2)},0,{str(ARIMA_q_2)})')
        if wind_velocity_at_T_minus_prediction_horizon is True:
            plt.plot(residuals_t_minus_x, label = f'residuals_t_minus_{prediction_horizon}')
        plt.legend(fontsize=12)
        plt.title('Residuals from W_axis rolling Wind Prediction', fontsize=20)
        plt.ylabel('Error', fontsize=16)
        plt.axhline(0, color='r', linestyle='--', alpha=0.2)





# fit_and_forecast(file_name = 'raspberry/data/wind_data/25-09-23--16-49/25-09-23--16-49_N_10.csv',
#                  train_end = 35000,
#                  test_end = 35100,
#                  prediction_horizon = 5,
#                  ARIMA_p_1 = 6,
#                  ARIMA_d_1 = 0,
#                  ARIMA_q_1 = 6,
#                  ARIMA_p_2 = None,
#                  ARIMA_d_2 = None,
#                  ARIMA_q_2 = None,
#                  wind_velocity_at_T_minus_prediction_horizon = True,
#                  combined_wind_speed = True,
#                  U = False,
#                  V = False,
#                  W = False)

fix_params_and_forecast(file_name = 'raspberry/data/wind_data/25-09-23--16-49/25-09-23--16-49_N_10.csv',
                        train_end = 20,
                        test_end = 10000,
                        prediction_horizon = 10,
                        ARIMA_p_1 = 5,
                        ARIMA_d_1 = 0,
                        ARIMA_q_1 = 8,
                        fix_params_1 = {'ar.L1' : 1.572654,
                                        'ar.L2' : -1.193433,
                                        'ar.L3' : 0.9085445,
                                        'ar.L4' : -0.5089323,
                                        'ar.L5' : 0.2081693,
                                        'ma.L1' : -0.0713252,
                                        'ma.L2' : 0.9297537,
                                        'ma.L3' : 0.0202807,
                                        'ma.L4' : 0.8987153,
                                        'ma.L5' : -0.0014764,
                                        'ma.L6' : 0.9206075,
                                        'ma.L7' : 0.0372892,
                                        'ma.L8' : 0.8512221},
                        ARIMA_p_2 = None,
                        ARIMA_d_2 = None,
                        ARIMA_q_2 = None,
                        fix_params_2 = None,
                        wind_velocity_at_T_minus_prediction_horizon = True,
                        combined_wind_speed = False,
                        U = True,
                        V = False,
                        W = False)


plt.show()
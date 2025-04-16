import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import csv
from statsmodels.tsa.statespace.sarimax import SARIMAX
from time import time

class ARIMA:
    def __init__(self, prediction_horizon, p, d, q, fix_params=None):
        self.prediction_horizon = prediction_horizon
        self.p = p
        self.d = d
        self.q = q
        self.fix_params = fix_params
        self.model_fit = None

    def fit(self, train_data):
        self.model = SARIMAX(train_data, order=(self.p, self.d, self.q))
        if self.fix_params is None:
            self.model_fit = self.model.fit(disp=False) 
        else:
            with self.model.fix_params(self.fix_params):
                self.model_fit = self.model.fit(disp=False)
        return self.model_fit.params
    
    def update_params(self, new_data):
        new_model = SARIMAX(new_data, order=(self.p, self.d, self.q))
        new_model_fit = new_model.fit(disp=False)
        self.model_fit = new_model_fit
        self.fix_params = {'ar.L1' : new_model_fit.params[0],
                           'ar.L2' : new_model_fit.params[1],
                           'ar.L3' : new_model_fit.params[2],
                           'ar.L4' : new_model_fit.params[3],
                           'ar.L5' : new_model_fit.params[4],
                           'ar.L6' : new_model_fit.params[5],
                           'ar.L7' : new_model_fit.params[6],
                           'ar.L8' : new_model_fit.params[7],
                           'ar.L9' : new_model_fit.params[8],
                           'ma.L1' : new_model_fit.params[9],
                           'ma.L2' : new_model_fit.params[10],
                           'ma.L3' : new_model_fit.params[11]}
        print(f'new_params = {self.fix_params}')

    def predict(self, new_data_point):
        # Update model state directly using Kalman filtering without full re-fit
        self.model_fit = self.model_fit.extend(new_data_point)
        
        # Directly generate the next prediction
        prediction = self.model_fit.get_forecast(steps=self.prediction_horizon).predicted_mean[-1]
        return prediction

    def multi_step_predictions(self, new_data_point):
        # Update model state directly using Kalman filtering without full re-fit
        self.model_fit = self.model_fit.extend(new_data_point)
        
        # Directly generate the next prediction
        predictions = self.model_fit.get_forecast(steps=self.prediction_horizon).predicted_mean
        return predictions

    def plot_predictions(self, train_data, test_data, predictions):
        plt.figure(figsize=(10, 6))
        plt.plot(train_data, label='Training Data')
        plt.plot(range(len(train_data), len(train_data) + len(test_data)), test_data, label='Test Data')
        plt.plot(range(len(train_data) + self.prediction_horizon, len(train_data) + len(predictions) + self.prediction_horizon,), predictions, label='Predictions')
        plt.legend(fontsize=12)
        plt.title(f'ARIMA({str(self.p)},{str(self.d)},{str(self.q)}) Predictions', fontsize=20)
        plt.xlabel('Time step', fontsize=16)
        plt.ylabel('Wind Speed (m/s)', fontsize=16)
        plt.show()

def run_arima_model(file_name,
                    train_end, 
                    test_end, 
                    prediction_horizon, 
                    p, 
                    d, 
                    q, 
                    fix_params=None,
                    combined_wind_speed: bool = False,
                     U: bool = False,
                     V: bool = False,
                     W: bool = False,
                     logger = False):
    sample_time = 0.025
    prediction_time = prediction_horizon * sample_time
    
    if combined_wind_speed is True:
        df_wind = pd.read_csv(f'{file_name}.csv', usecols=[3])
        last_step_prediction = np.array([])
        combined_step_errors = pd.Series()
        x=0
        sum_of_squares = 0

        train_data = df_wind.values[:train_end]
        test_data = df_wind.values[train_end:test_end]
        model = ARIMA(prediction_horizon=prediction_horizon, p=p, d=d, q=q, fix_params=fix_params)
        model.fit(train_data)

        # Make predictions
        for i in test_data[:-prediction_horizon]:
            temp_test = test_data[x+1: x+prediction_horizon+1]
            last_step_prediction = np.append(last_step_prediction,model.predict([i]))
            multi_step_predictions =model.multi_step_predictions([i])
            sum_of_squares = sum_of_squares + (sum(sum((temp_test.T - multi_step_predictions)**2)))
            combined_step_errors[x] = np.sqrt(sum(sum((temp_test.T - multi_step_predictions)**2))/prediction_horizon)
            x = x + 1
        last_step_prediction = last_step_prediction.reshape(-1, 1)

        test_data = test_data[prediction_horizon:]
    
        last_step_RMSE = np.sqrt(np.mean((test_data - last_step_prediction)**2))

        last_step_error = np.sqrt((test_data - last_step_prediction)**2)
        last_step_quantile_error = np.quantile(last_step_error, 0.95)

        combined_RMSE = np.sqrt(sum_of_squares/(len(test_data)*prediction_horizon))

        combined_quantile_errors = np.quantile(combined_step_errors, 0.95)

        if logger is True:
            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_combined_wind_speed_last_step_RMSE.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', last_step_RMSE])
            
            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_combined_wind_speed_last_step_quantile_error.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', last_step_quantile_error])

            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_combined_wind_speed_combined_RMSE.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', combined_RMSE])

            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_combined_wind_speed_combined_quantile_errors.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', combined_quantile_errors])

    if U is True:
        df_wind = pd.read_csv(f'{file_name}.csv', usecols=[7])
        last_step_prediction = np.array([])
        combined_step_errors = pd.Series()
        x=0
        sum_of_squares = 0

        train_data = df_wind.values[:train_end]
        test_data = df_wind.values[train_end:test_end]
        model = ARIMA(prediction_horizon=prediction_horizon, p=p, d=d, q=q, fix_params=fix_params)
        model.fit(train_data)

        # Make predictions
        for i in test_data[:-prediction_horizon]:
            temp_test = test_data[x+1: x+prediction_horizon+1]
            last_step_prediction = np.append(last_step_prediction,model.predict([i]))
            multi_step_predictions =model.multi_step_predictions([i])
            sum_of_squares = sum_of_squares + (sum(sum((temp_test.T - multi_step_predictions)**2)))
            combined_step_errors[x] = np.sqrt(sum(sum((temp_test.T - multi_step_predictions)**2))/prediction_horizon)
            x = x + 1
        last_step_prediction = last_step_prediction.reshape(-1, 1)

        test_data = test_data[prediction_horizon:]
    
        last_step_RMSE = np.sqrt(np.mean((test_data - last_step_prediction)**2))

        last_step_error = np.sqrt((test_data - last_step_prediction)**2)
        last_step_quantile_error = np.quantile(last_step_error, 0.95)

        combined_RMSE = np.sqrt(sum_of_squares/(len(test_data)*prediction_horizon))

        combined_quantile_errors = np.quantile(combined_step_errors, 0.95)

        if logger is True:
            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_U_last_step_RMSE.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', last_step_RMSE])
            
            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_U_last_step_quantile_error.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', last_step_quantile_error])

            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_U_combined_RMSE.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', combined_RMSE])

            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_U_combined_quantile_errors.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', combined_quantile_errors])

    if V is True:
        df_wind = pd.read_csv(f'{file_name}.csv', usecols=[8])
        last_step_prediction = np.array([])
        combined_step_errors = pd.Series()
        x=0
        sum_of_squares = 0
        update_every = 12000
        how_far_back = update_every

        train_data = df_wind.values[:train_end]
        test_data = df_wind.values[train_end:test_end]
        model = ARIMA(prediction_horizon=prediction_horizon, p=p, d=d, q=q, fix_params=fix_params)
        model.fit(train_data)
        print(f'model_fit params = {model.model_fit.params}')
        # with open(f'V_PARAMS.csv', "a+", newline="") as f:
        #                 # creating the writer
        #                 writer = csv.writer(f)
        #                 # using writerow to write individual record one by one
        #                 writer.writerow([model_fit])

        # Make predictions
        for i in test_data[:-prediction_horizon]:
            if (x+1) % update_every == 0:
                start = time()
                model.update_params(test_data[x+1-how_far_back:x+1])
                print(f'update time = {time() - start}')
                how_far_back = int(0.2*update_every)
                # if x < 4000:
                #     how_far_back = how_far_back + update_every
                # print(f'how_far_back = {how_far_back}')
            temp_test = test_data[x+1: x+prediction_horizon+1]
            last_step_prediction = np.append(last_step_prediction,model.predict([i]))
            multi_step_predictions =model.multi_step_predictions([i])
            sum_of_squares = sum_of_squares + (sum(sum((temp_test.T - multi_step_predictions)**2)))
            combined_step_errors[x] = np.sqrt(sum(sum((temp_test.T - multi_step_predictions)**2))/prediction_horizon)
            x = x + 1
        last_step_prediction = last_step_prediction.reshape(-1, 1)

        # model.plot_predictions(train_data, test_data, last_step_prediction)

        test_data = test_data[prediction_horizon:]
    
        last_step_RMSE = np.sqrt(np.mean((test_data - last_step_prediction)**2))
        print(f'last_step_RMSE: {last_step_RMSE}')

        last_step_error = np.sqrt((test_data - last_step_prediction)**2)
        print(f'last_step_error: {last_step_error}')

        #save error to csv
        # last_step_error = pd.Series(last_step_error)
        last_step_error_pd = pd.DataFrame(last_step_error, columns=['error'])
        last_step_error_pd.to_csv(f'{file_name.split(".")[0]}_error.csv', index=False)


        last_step_quantile_error = np.quantile(last_step_error, 0.95)
        print(f'last_step_quantile_error: {last_step_quantile_error}')

        combined_RMSE = np.sqrt(sum_of_squares/(len(test_data)*prediction_horizon))

        combined_quantile_errors = np.quantile(combined_step_errors, 0.95)

        plt.figure(figsize=(10,4))
        sns.distplot(last_step_error, hist=False, color='blue')
        sns.distplot(combined_step_errors, hist=False, color='red')
        plt.plot([last_step_RMSE, last_step_RMSE], [0, 1], color='darkblue')
        plt.plot([combined_RMSE, combined_RMSE], [0, 1], color='firebrick')
        plt.text(last_step_RMSE, 0.5, f'RMSE: {last_step_RMSE:.2f}', color='darkblue', fontsize=12, ha='center')
        plt.text(combined_RMSE, 0.5, f'RMSE: {combined_RMSE:.2f}', color='firebrick', fontsize=12, ha='center')
        plt.plot([last_step_quantile_error, last_step_quantile_error], [0, 1], color='darkblue')
        plt.plot([combined_quantile_errors, combined_quantile_errors], [0, 1], color='firebrick')
        plt.text(last_step_quantile_error, 0.5, f'95% Quantile \n Error: {last_step_quantile_error:.2f}', color='darkblue', fontsize=12, ha='center')
        plt.text(combined_quantile_errors, 0.5, f'95% Quantile \n Error: {combined_quantile_errors:.2f}', color='firebrick', fontsize=12, ha='center')
        plt.title(f'Probability Density Error of ARIMA({str(p)},{str(d)},{str(q)} using {prediction_horizon} steps ({prediction_time} seconds) forecast', fontsize=20)
        plt.legend((f'Error only using the last step forecast',
                    f'Error for all the steps in the forecast'), fontsize=12)
        plt.ylabel('Probability Density', fontsize=16)
        plt.xlabel('Error (m/s)', fontsize=16)
        plt.show()

        if logger is True:
            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_V_last_step_RMSE.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', last_step_RMSE])
            
            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_V_last_step_quantile_error.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', last_step_quantile_error])

            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_V_combined_RMSE.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', combined_RMSE])

            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_V_combined_quantile_errors.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', combined_quantile_errors])

    if W is True:
        df_wind = pd.read_csv(f'{file_name}.csv', usecols=[9])
        last_step_prediction = np.array([])
        combined_step_errors = pd.Series()
        x=0
        sum_of_squares = 0

        train_data = df_wind.values[:train_end]
        test_data = df_wind.values[train_end:test_end]
        model = ARIMA(prediction_horizon=prediction_horizon, p=p, d=d, q=q, fix_params=fix_params)
        model.fit(train_data)

        # Make predictions
        for i in test_data[:-prediction_horizon]:
            temp_test = test_data[x+1: x+prediction_horizon+1]
            last_step_prediction = np.append(last_step_prediction,model.predict([i]))
            multi_step_predictions =model.multi_step_predictions([i])
            sum_of_squares = sum_of_squares + (sum(sum((temp_test.T - multi_step_predictions)**2)))
            combined_step_errors[x] = np.sqrt(sum(sum((temp_test.T - multi_step_predictions)**2))/prediction_horizon)
            x = x + 1
        last_step_prediction = last_step_prediction.reshape(-1, 1)

        test_data = test_data[prediction_horizon:]
    
        last_step_RMSE = np.sqrt(np.mean((test_data - last_step_prediction)**2))

        last_step_error = np.sqrt((test_data - last_step_prediction)**2)
        last_step_quantile_error = np.quantile(last_step_error, 0.95)

        combined_RMSE = np.sqrt(sum_of_squares/(len(test_data)*prediction_horizon))

        combined_quantile_errors = np.quantile(combined_step_errors, 0.95)

        if logger is True:
            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_W_last_step_RMSE.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', last_step_RMSE])
            
            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_W_last_step_quantile_error.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', last_step_quantile_error])

            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_W_combined_RMSE.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', combined_RMSE])

            with open(f'{file_name}_Simple_ARMA_{train_end}-{test_end}_W_combined_quantile_errors.csv', "a+", newline="") as f:
                        # creating the writer
                        writer = csv.writer(f)
                        # using writerow to write individual record one by one
                        writer.writerow([f'({str(p)},{str(d)},{str(q)})', combined_quantile_errors])    

# Example usage
if __name__ == "__main__":

    # for i in range(11,21):
    #     for j in range(21):   
            run_arima_model(file_name='raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10',
                            train_end=400,
                            test_end=39370,
                            prediction_horizon=10,
                            p=9,
                            d=0,
                            q=3,
                            # fix_params=None,
                            fix_params = {'ar.L1' : 0.85555221,
                                          'ar.L2' : 0.9949465,
                                          'ar.L3' : -0.30541855,
                                          'ar.L4' : -0.93379016,
                                          'ar.L5' : 0.30228411,
                                          'ar.L6' : 0.16281163,
                                          'ar.L7' : -0.10295508,
                                          'ar.L8' : -0.17064146,
                                          'ar.L9' : 0.19521308,
                                          'ma.L1' : 0.7767682,
                                          'ma.L2' : -0.33131051,
                                          'ma.L3' : -0.73381169},
                            combined_wind_speed=False,
                            U=False,
                            V=True,
                            W=False,
                            logger=False)

    # sample_time = 0.025
    # prediction_horizon = 10
    # last_step_prediction = np.array([])
    # combined_step_errors = pd.Series()
    # prediction_time = prediction_horizon * sample_time
    # x=0
    # sum_of_squares = 0
    # p = 5
    # d = 0
    # q = 8
    # # Read Data
    # df_wind = pd.read_csv('raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10.csv', usecols=[3])
    # train_data = df_wind.values[:1000]
    # test_data = df_wind.values[1000:1100 + prediction_horizon]

    # # Initialize and fit the model
    # model = ARIMA(prediction_horizon=prediction_horizon, p=p, d=d, q=q)
    # model.fit(train_data)

    # # Make predictions
    # for i in test_data[:-prediction_horizon]:
    #     temp_test = test_data[x+1: x+prediction_horizon+1]
    #     last_step_prediction = np.append(last_step_prediction,model.predict([i]))
    #     multi_step_predictions =model.multi_step_predictions([i])
    #     sum_of_squares = sum_of_squares + (sum(sum((temp_test.T - multi_step_predictions)**2)))
    #     combined_step_errors[x] = np.sqrt(sum(sum((temp_test.T - multi_step_predictions)**2))/prediction_horizon)
    #     x = x + 1
    # last_step_prediction = last_step_prediction.reshape(-1, 1)

    # # Plot the results
    # model.plot_predictions(train_data, test_data, last_step_prediction)

    # test_data = test_data[prediction_horizon:]
    
    # last_step_RMSE = np.sqrt(np.mean((test_data - last_step_prediction)**2))
    # print(f'last_step_RMSE: {last_step_RMSE}')

    # last_step_error = np.sqrt((test_data - last_step_prediction)**2)
    # last_step_quantile_error = np.quantile(last_step_error, 0.95)
    # print(f'last_step_quantile_error: {last_step_quantile_error}')

    # combined_RMSE = np.sqrt(sum_of_squares/(len(test_data)*prediction_horizon))
    # print(f'combined_RMSE: {combined_RMSE}')

    # combined_quantile_errors = np.quantile(combined_step_errors, 0.95)
    # print(f'combined_quantile_errors: {combined_quantile_errors}')

    # plt.figure(figsize=(10,4))
    # sns.distplot(last_step_error, hist=False, color='blue')
    # sns.distplot(combined_step_errors, hist=False, color='red')
    # plt.plot([last_step_RMSE, last_step_RMSE], [0, 1], color='darkblue')
    # plt.plot([combined_RMSE, combined_RMSE], [0, 1], color='firebrick')
    # plt.text(last_step_RMSE, 0.5, f'RMSE: {last_step_RMSE:.2f}', color='darkblue', fontsize=12, ha='center')
    # plt.text(combined_RMSE, 0.5, f'RMSE: {combined_RMSE:.2f}', color='firebrick', fontsize=12, ha='center')
    # plt.plot([last_step_quantile_error, last_step_quantile_error], [0, 1], color='darkblue')
    # plt.plot([combined_quantile_errors, combined_quantile_errors], [0, 1], color='firebrick')
    # plt.text(last_step_quantile_error, 0.5, f'95% Quantile \n Error: {last_step_quantile_error:.2f}', color='darkblue', fontsize=12, ha='center')
    # plt.text(combined_quantile_errors, 0.5, f'95% Quantile \n Error: {combined_quantile_errors:.2f}', color='firebrick', fontsize=12, ha='center')
    # plt.title(f'Probability Density Error of ARIMA({str(p)},{str(d)},{str(q)} using {prediction_horizon} steps ({prediction_time} seconds) forecast', fontsize=20)
    # plt.legend((f'Error only using the last step forecast',
    #             f'Error for all the steps in the forecast'), fontsize=12)
    # plt.ylabel('Probability Density', fontsize=16)
    # plt.xlabel('Error (m/s)', fontsize=16)
    # plt.show()

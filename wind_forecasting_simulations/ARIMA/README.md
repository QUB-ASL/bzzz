# ARIMA
The following python files make use of the Python module [statsmodels](https://www.statsmodels.org/stable/index.html).

For each 'forecast' script we start by plotting the data of interest against time. Next the ACF and PACF are plotted as these give a good 
indicator to the order of the model. The data is then split up into training data and test data. The model is then defined with order
to be used and then fit to the training data. After the model is fit various types of predictions are then carried out depending on what 
script is ran. Forecast errors are also carried out to determine how good the forecasts are compared to the actual data or just using
the previous time sample.

## `Long_forecast.py` 
The 'long forecast' is the most simple forecast where it tries to predict the next value at each time sample in the test data without 
updating the data available to the model. The residuals of the prediction compared to the test data is also plotted. The same predictions
and residuals are then carried out for the first and second differences of the wind data. This script is useful for visually seeing how
the prediction deteriorates over time for each model while the data isn't updated.

## `forecast.py`
In this script, at each time sample a value for a set number of forecasts into the future is predicted (e.g. predict(t+5) for predicting
5 steps/samples ahead) and plotted. At each time sample the data set is also updated where it is given the actual wind data for the 
previous time sample. The model parameters are currently kept the same but there is the option to update the model when given new data. 
The residuals of the prediction compared to the test data is also plotted.

## `multi_forecast.py`
This script is similar to the `forecast.py` script except at each time sample rather than just the prediction of interest being plotted, 
all the predictions are plotted from predict(t+1) to predict(t+x). This is useful as it shows how forecasting further into the future 
effects the prediction. he root-mean-square error (RMSE) of the model is also determined and plotted along with the quantile error.

## `prediction_error.py`
The 'prediction error' script is used to validate the ARIMA model. The root-mean-square error (RMSE) is determined for the model and 
a quantile error (usually 95%) determined to give a value that can be compared between models to determine which one is better. This
script can be used to save the quantile error of many models for different wind values so the user can determine which model is best.


# Wind Forecasting  
This folder includes different methods for trying to predict/forecast future wind disturbances.

It uses wind data that has been collected using the Trisonica mini anemometer and can be found under `raspberry/anemometer/wind_data`. 


## ARIMA
This folder incudes different ARIMA based methods for model fitting and forecasting along with a prediction error script 
for validation the model used for the prediction.


## Wind data 
This is open source wind data which can be found [here](https://data.mendeley.com/datasets/jdjmg8s544/2), 
which was used before are own wind data was recorded.


## `plot_wind_data.py`
This is a simple python script for plotting four separate graphs of the 'wind speed' (magnitude of the total 3D wind speed), 
'U axis', 'V axis' and 'W axis' against time along with there associated ACF and PACF graphs. 


## `Data_editor.py`
This script is for changing the sample frequency of recorded wind data. 
The wind data is all recorded at as high as frequency as possible (40Hz). 
This script changes the frequency of the recorded wind data by averaging the wind speed and direction and saves it as a new csv file. 

## `Correlogram.py`
This script is for checking the correlation of the wind data (e.g. Wind_Speed) at time 't' against 
the wind data at a previous time 't-x'.

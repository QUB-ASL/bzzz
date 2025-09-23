# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import csv
# import datetime

# def DataEditor(file_name):

#     #read data
#     df_wind = pd.read_csv(f'{file_name}.csv')
    
#     res = pd.DataFrame({'A' : []})

#     # res['Index'] = df_wind['index']
#     res['Date_Time'] = df_wind['Date_Time']
#     res['Wind_Speed'] = df_wind['Wind_Speed']
#     res['Wind_Speed_2D'] = df_wind['Wind_Speed_2D']
#     res['H_direction'] = df_wind['H_direction']
#     res['V_direction'] = df_wind['V_direction']
#     res['U_axis'] = df_wind['U_axis']
#     res['V_axis'] = df_wind['V_axis']
#     res['W_axis'] = df_wind['W_axis']

#     res['Index_2'] = datetime.datetime(2000, 1, 1, 0, 0, 0, 000000)

#     for x in range(157640): 
#       res['Index_2'][x+1] = res['Index_2'][x] + datetime.timedelta(seconds=0.025)  

#         # res['Index_2'] = df_wind.Date_Time
    
#     # temp_time = datetime.datetime(2023, 12, 21, 20, 48, 31, 000000)

#     # for x in range(24001):
#     #   temp_time = temp_time + datetime.timedelta(seconds=0.025)  
#     #   res['Index_2'][x] = temp_time

#     res = res[["Index_2","Date_Time", "Wind_Speed", "Wind_Speed_2D", "H_direction", "V_direction", "U_axis", "V_axis", "W_axis"]]
    
#     #set index
#     # res.index = pd.date_range(res.Index_2[0], res.Index_2.iloc[-1], freq="25L")
    
#     #save file
#     res.to_csv(f'{file_name}.csv', index=False)


# DataEditor(file_name='raspberry/data/wind_data/december_2023/21-12-23--17-24/21-12-23--17-24_N_10')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

def DataEditor(file_name):
    # Read data
    df_wind = pd.read_csv(f'{file_name}.csv')

    # Copy required columns directly
    res = df_wind[['Date_Time', 'Wind_Speed', 'Wind_Speed_2D',
                   'H_direction', 'V_direction', 'U_axis', 'V_axis', 'W_axis']].copy()

    # Create a datetime range starting from 2000-01-01 with 0.025s interval
    start_time = datetime.datetime(2000, 1, 1)
    time_index = [start_time + datetime.timedelta(seconds=0.025 * i) for i in range(len(res))]
    res['Index_2'] = time_index

    # Reorder columns
    res = res[["Index_2", "Date_Time", "Wind_Speed", "Wind_Speed_2D",
               "H_direction", "V_direction", "U_axis", "V_axis", "W_axis"]]

    # Save to new CSV to avoid overwriting original
    res.to_csv(f'{file_name}_edited.csv', index=False)

# Run function
DataEditor(file_name='raspberry/data/wind_data/16-09-23--18-35/16-09-23--18-35_N_10')

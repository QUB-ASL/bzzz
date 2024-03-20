from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv


#read data
df = pd.read_csv('Anemometer.csv')

res = df

res['timestamp'] = 0

for x in range(1,3361):
    res.timestamp[x] = datetime.timestamp(pd.to_datetime(res.Date_Time.values[x])) - datetime.timestamp(pd.to_datetime(res.Date_Time.values[0]))

res = res[::10]

#save file
res.to_csv('Anemometer.csv')


# from datetime import datetime
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import csv


# #read data
# df = pd.read_csv('All_data.csv')

# res = df[['timestamp','KF_beta_est']].copy()


# #save file
# res.to_csv('KF_beta_est.csv')
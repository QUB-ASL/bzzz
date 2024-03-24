# from datetime import datetime
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import csv


# #read data
# df = pd.read_csv('Evo-ToF-15-03-24--16-44.csv')

# res = df

# res['timestamp'] = 0

# for x in range(1,12573):
#     res.timestamp[x] = datetime.timestamp(pd.to_datetime(res.Date_Time.values[x])) - datetime.timestamp(pd.to_datetime(res.Date_Time.values[0]))
#     res.timestamp[x] = res.timestamp[x] * 1000

# res = res[::10]

# #save file
# res.to_csv('EvoNNEEEWWW-ToF-15-03-24--16-44.csv')


from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv


#read data
df = pd.read_csv('altitude_ref.csv')

res = df

for x in range(0,356):
    res.altitude_ref[x] = float(res.altitude_ref[x])
    

res = df[['timestamp','altitude_ref']].copy()


#save file
res.to_csv('altitude_ref.csv')
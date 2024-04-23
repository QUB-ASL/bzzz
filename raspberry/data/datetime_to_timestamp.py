from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv


#read data
filename = "PressureSensor-22-04-24--13-46"
df = pd.read_csv(f"{filename}.csv")

res = df

res['timestamp'] = 0

for x in range(1,1943):
    res.timestamp[x] = datetime.timestamp(pd.to_datetime(res.Date_Time.values[x])) - datetime.timestamp(pd.to_datetime(res.Date_Time.values[0]))

#save file
res.to_csv(f"{filename}_NEW.csv")

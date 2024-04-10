from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv


#read data
df = pd.read_csv('BB-09-04-24--18-50.csv')

res = df

for x in range(0,430):
    res.tau[x] = res.tau[x] + 0.9
    res.v_hat[x] = res.v_hat[x] + 0.75

#save file
res.to_csv('BB-09-04-24--18-50_NEW.csv')
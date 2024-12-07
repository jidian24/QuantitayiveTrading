# test vectorbt
import numpy as np
import pandas as pd
import vectorbt as vbt
import matplotlib.pyplot as plt

df_ohlcv = pd.read_csv('..//data//Gate.io_ACA_swap_1d.csv',index_col=0,parse_dates=True)  # 表格列名：datetime,open,hight,low,volume
close=df_ohlcv['close']
# plt.plot(close, label='Close Price')
10 # Calculate the standard deviation of the columns in df
fig = vbt.MSTD.run(close,  10).plot()

# plt.show()
# plt.show()
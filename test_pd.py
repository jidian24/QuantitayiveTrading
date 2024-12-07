import pandas as pd
import vectorbt as vbt
import matplotlib.pyplot as plt

df_ohlcv = pd.read_csv('..//data//Gate.io_ACA_swap_1d.csv', index_col=0, parse_dates=True)
close = df_ohlcv['close']

# 计算ATR指标
mstd = vbt.MSTD.run(close, window=10)
mstd.msts
plt.plot(mstd)
plt.title('Mean Standard Deviation')
plt.xlabel('Time')
plt.ylabel('MSTD')
plt.tight_layout()
plt.show()
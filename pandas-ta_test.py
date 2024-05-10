import pandas as pd
import pandas_ta as ta

# Load data
df = pd.read_csv("gateio_ABT_USDT_1d.csv", sep=",")
df1=df.copy()

df1.ta.strategy('all')

print(df1.columns)
# Runs and appends all indicators to the current DataFrame by default
# The resultant DataFrame will be large.
df.ta.strategy()
# Or the string "all"
df.ta.strategy("all")
# Or the ta.AllStrategy
df.ta.strategy(ta.AllStrategy)

# Use verbose if you want to make sure it is running.
df.ta.strategy(verbose=True)

# Use timed if you want to see how long it takes to run.
df.ta.strategy(timed=True)

# Maybe you do not want certain indicators.
# Just exclude (a list of) them.
df.ta.strategy(exclude=["bop", "mom", "percent_return", "wcp", "pvi"], verbose=True)

# Perhaps you want to use different values for indicators.
# This will run ALL indicators that have fast or slow as parameters.
# Check your results and exclude as necessary.
df.ta.strategy(fast=10, slow=50, verbose=True)

# Sanity check. Make sure all the columns are there
df.columns







# Load data
df = pd.read_csv("gateio_ABT_USDT_1d.csv", sep=",")

# Calculate Returns and append to the df DataFrame
df.ta.log_return(cumulative=True, append=True)
df.ta.percent_return(cumulative=True, append=True)

# New Columns with results
df.columns

# Take a peek
df.tail()





# pandas-ta 的 ta.Strategy 的简单示例，该示例基于简单的移动平均线交叉策略
import pandas as pd  
import pandas_ta as ta  
  
# 假设你有一个包含 'Close' 列的 DataFrame 'df'  
# df = pd.read_csv('your_data.csv')  # 例如，从 CSV 文件中读取数据  
  
# 为了示例，我们创建一个简单的 DataFrame  
dates = pd.date_range(start="2023-01-01", periods=100)  
data = {'Close': (100 + (pd.Series(range(100)) + pd.Series(range(100)).cumsum() * 0.1)).cumsum()}  
df = pd.DataFrame(data, index=dates)  
  
# 添加简单移动平均线到 DataFrame  
df['SMA_short'] = ta.sma(df['Close'], length=7)  
df['SMA_long'] = ta.sma(df['Close'], length=21)  
  
# 定义策略  
strategy = {  
    'SMA Crossover': {  
        'longentry': df['SMA_short'] > df['SMA_long'],  
        'longexit': df['SMA_short'] < df['SMA_long'],  
        'shortentry': False,  # 在这个策略中我们不考虑空头  
        'shortexit': False,  # 在这个策略中我们不考虑空头  
    }  
}  
  
# 应用策略并添加信号列到 DataFrame  
signals = ta.strategy(df, strategy)  
df = pd.concat([df, signals], axis=1)  
  
# 查看结果  
print(df.tail())





#-------------------------------------
import pandas as pd
import pandas_ta as ta
# The Builtin All Default Strategy
ta.AllStrategy = ta.Strategy(
    name="All",
    description="All the indicators with their default settings. Pandas TA default.",
    ta=None
)

# The Builtin Default (Example) Strategy.
ta.CommonStrategy = ta.Strategy(
    name="Common Price and Volume SMAs",
    description="Common Price SMAs: 10, 20, 50, 200 and Volume SMA: 20.",
    ta=[
        {"kind": "sma", "length": 10},
        {"kind": "sma", "length": 20},
        {"kind": "sma", "length": 50},
        {"kind": "sma", "length": 200},
        {"kind": "sma", "close": "volume", "length": 20, "prefix": "VOL"}
    ]
)

# Your Custom Strategy or whatever your TA composition
CustomStrategy = ta.Strategy(
    name="Momo and Volatility",
    description="SMA 50,200, BBANDS, RSI, MACD and Volume SMA 20",
    ta=[
        {"kind": "sma", "length": 50},
        {"kind": "sma", "length": 200},
        {"kind": "bbands", "length": 20},
        {"kind": "rsi"},
        {"kind": "macd", "fast": 8, "slow": 21},
        {"kind": "sma", "close": "volume", "length": 20, "prefix": "VOLUME"},
    ]
)






#模块和指示器帮助文档
#---------------------------------------------
import pandas as pd
import pandas_ta as ta

# Help about this, 'ta', extension
help(pd.DataFrame().ta)

# List of all indicators
pd.DataFrame().ta.indicators()

# Help about the log_return indicator
help(ta.log_return)




#------------------------------------------












# SMA指标的交易策略回测程序
import pandas as pd  
import pandas_ta as ta  
import numpy as np  
  
# 读取CSV文件  
file_name = 'gateio_ABT_USDT_1d.csv'  
df = pd.read_csv(file_name)  
  
# 假设CSV文件包含'close'列作为收盘价  
# 确保数据按日期排序  
df.sort_index(inplace=True)  
  
# 设置SMA的窗口大小  
short_window = 7  
long_window = 21  
  
# 计算SMA  
df['SMA_short'] = ta.sma(df['close'], length=short_window)  
df['SMA_long'] = ta.sma(df['close'], length=long_window)  
  
# 生成交易信号  
df['Signal'] = 0.0  
df['Signal'][short_window:] = np.where(df['SMA_short'][short_window:] > df['SMA_long'][short_window:], 1.0, 0.0)  
df['Positions'] = df['Signal'].diff()  
  
# 初始化持仓和现金  
cash = 10000.0  
positions = 0  
total_profit = 0  
holdings = 0  
  
# 回测逻辑  
for index, row in df.iloc[short_window:].iterrows():  
    if row['Positions'] == 1:  # 进入多头  
        if positions == 0:  
            positions = cash / row['close']  
            cash = 0  
    elif row['Positions'] == -1:  # 进入空头（这里我们不考虑空头，所以跳过）  
        continue  
    elif row['Positions'] == 0:  # 平仓  
        if positions != 0:  
            cash += positions * row['close']  
            positions = 0  
      
    # 计算持仓价值  
    holdings = positions * row['close'] if positions != 0 else 0  
      
    # 计算总利润  
    total_profit += cash + holdings - 10000.0  
      
    # 打印当前状态（可选）  
    print(f"Date: {index}, close: {row['close']}, Cash: {cash:.2f}, Positions: {positions:.2f}, Holdings: {holdings:.2f}, Total Profit: {total_profit:.2f}")  
  
# 打印最终利润  
print(f"Final Total Profit: {total_profit:.2f}")




#
import pandas as pd  
import pandas_ta as ta  
  
# 假设你有一个名为 df 的 DataFrame，其中 'close' 列包含收盘价  
df = pd.read_csv('gateio_ABT_USDT_1d.csv')  # 例如，从 CSV 文件中读取数据  
  
# 为了示例，我们创建一个简单的 DataFrame  
# dates = pd.date_range(start="2023-01-01", periods=100)  
# data = {'close': (100 + (pd.Series(range(100)) + pd.Series(range(100)).cumsum() * 0.1)).cumsum()}  
# df = pd.DataFrame(data, index=dates)  
  
# 计算短期和长期 SMA  
short_window = 5  
long_window = 20  
df['SMA_short'] = ta.sma(df['close'], length=short_window)  
df['SMA_long'] = ta.sma(df['close'], length=long_window)  
  
# 使用 ta.cross() 检测交叉信号  
df['Crossover_Signal'] = 0  
df['Crossover_Signal'][short_window:] = ta.cross(df['SMA_short'][short_window:], df['SMA_long'][short_window:], above=True)  
  
# 查看结果  
print(df.tail())
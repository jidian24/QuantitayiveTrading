import ccxt
import time
import pandas as pd
import numpy as np
from tqdm import tqdm
import sys


import os
"""
函数功能:获取并记录exchang变量指定的加密货币交易所全部永续合约交易对的资金费率。
要求1：DataFrame格式定义：行名记录时间，列名表示交易对名称。
要求2：本程序涉及网络连接必须考虑容错机制，网络异常的情况程序能继续运行。
流程及逻辑：
1. 读入已有的'get_futures_funding_rate.csv'文件内容到DataFrame。
2. 用ccxt库获取全部exchang变量指定的加密货币交易所全部永续合约交易对列表；
3. 循环获取每一个交易对的当前资金费率及下次资金费率应用时间，并逐个赋值到-行名为：下次资金费率应用时间，列名为：交易对名称 的DataFrame单元格。要求程序提前判断是否已存在同名的行或列，如果无则新建行名或列名。
4. 求DataFrame末行的最大值，并赋值到末行，'max'列名的单元格。
5. DataFrame写入到文件：get_futures_funding_rate.csv
6. 以每天的时间0.00开始每4小时开闸一次，计算下一次开闸的UTC时间。
"""
def get_futures_funding_rate_csv(exchange):
    # 读入已有的'get_futures_funding_rate.csv'文件内容到DataFrame
    if os.path.exists('get_futures_funding_rate.csv'):
        df = pd.read_csv('get_futures_funding_rate.csv', index_col=0)
    else:
        df = pd.DataFrame()
    # 计算下一个4小时整除的开闸时间
    next_rate_timestamp = (int(time.time()) // 14400 + 1) * 14400
    # 用ccxt库获取全部exchange指定的加密货币交易所全部永续合约交易对列表
    exchange_obj = getattr(ccxt, exchange)()
    markets = exchange_obj.fetch_markets()
    
    for market in markets:
        symbol = market['symbol']
        try:
            if market['swap']:  # 判断是否为永续合约市场
                funding_rate = exchange_obj.fetch_funding_rate(symbol)
                # 获取时间并格式
                next_funding_time = (int(funding_rate['info']['funding_next_apply']))
                if next_funding_time == next_rate_timestamp:
                    next_funding_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_funding_time))
                    rate = '{:.5f}'.format(funding_rate['nextFundingRate'])
                    symbol=symbol.split(':')[0]
                    # 判断是否已存在同名的行或列，如果无则新建行名或列名
                    if symbol not in df.columns:
                        df[symbol] = np.nan
                    if next_funding_time not in df.index:
                        df.loc[next_funding_time] = np.nan
                    # print(rate) 
                    rate=float(rate)
                    if abs(rate) > 0.00224:
                        print(f"go----- {symbol}: {rate}")
                    # 将资金费率赋值到DataFrame对应的单元格
                    df.loc[next_funding_time, symbol] = rate
        except Exception as e:
            print(f"Error fetching funding rate for {symbol}: {e}")
    
    # 求DataFrame末行的最大值，并赋值到末行，'max'列名的单元格
    min_value = df.iloc[-1].min()
    max_value = df.iloc[-1, 1:].max()
    last_row_index = df.shape[0] - 1
    last_column_index = df.shape[1] - 1
    # 将最大值赋值给最后一行最后一列+1的单元格
    df.loc[:, len(df)] = None  # 在DataFrame中新增一列，默认填充为None
    df.iloc[last_row_index, last_column_index + 1] = min_value
    df.loc[:, len(df)+1] = None  # 在DataFrame中新增一列，默认填充为None
    df.iloc[last_row_index, last_column_index + 2] = max_value
    
    # DataFrame写入到文件：get_futures_funding_rate.csv
    df.to_csv('get_futures_funding_rate.csv')
"""
程序功能：命令行传入参数启动，每天时间到4的整除点数开始执行get_futures_funding_rate_csv(exchange)功能函数
流程：
1. 在主程序中，获取命令行传入的参数，即交易所名称。
2. 定义一个循环，使程序每天在4的整数倍点提前2分钟开始执行get_futures_funding_rate_csv(exchange)函数。
3. 在循环中，获取当前时间，并判断是否为4的整数倍点。
4. 如果是4的整数倍点，则调用get_futures_funding_rate_csv(exchange)函数。
5. 程序休眠一段时间，等待下一个循环。
"""


# 获取命令行传入的参数，即交易所名称
if len(sys.argv) < 2:
    print("Usage: python get_futures_funding_rate_csv.py gate")
    sys.exit(1)

exchange = sys.argv[1]

# 定义一个循环，使程序每天在4的整数倍点开始执行get_futures_funding_rate_csv函数
while True:
    # 获取当前时间，并判断是否为4的整数倍点的前2分钟
    current_time = time.gmtime()  # 获取UTC标准时间
    if current_time.tm_hour % 4 == 0 and current_time.tm_min == 58 and current_time.tm_sec == 0:
        # 如果是4的整数倍点的前2分钟，则调用get_futures_funding_rate_csv函数
        get_futures_funding_rate_csv(exchange)
    
    # 计算距离下一次运行get_futures_funding_rate_csv函数还需等待多少时间
    remaining_time = (4 - (current_time.tm_hour % 4)) * 3600 - current_time.tm_min * 60 - current_time.tm_sec
    
    # 使用tqdm库展示进度条
    with tqdm(total=remaining_time, desc="Waiting") as pbar:
        for _ in range(remaining_time):
            time.sleep(1)
            pbar.update(1)
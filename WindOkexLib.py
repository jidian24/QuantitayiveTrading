#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import okx.MarketData as MarketData
import okx.PublicData as PublicData
import json
from itertools import chain 
import numpy as np
import pandas as pd
import os
import time
import datetime
from datetime import datetime, timedelta
import sys


api_key = "f0221edb-5d98-4148-8daa-94efc0d04b77"
secret_key = "7309250FBFE7893950AA3232BA42732E"
passphrase = "jidian24"
flag = '0'  # 实盘# flag是实盘与模拟盘的切换参数# flag = '1'  # 模拟盘
marketDataAPI = MarketData.MarketAPI(api_key, secret_key, passphrase, False, flag)
# marketDataAPI >> MarketAPI
# file operate
def list2txt(listdata, path_buffer):

    if listdata:
        with open(path_buffer, 'w') as f:
            f.write(str(listdata))

def txt2list(path_buffer):
    if os.path.exists(path_buffer) :
        with open(path_buffer, 'r') as f:
            listdata =  eval(f.read())
    return listdata

def csv_add(path_buffer, df): # 添加到csv
    df_ed = pd.read_csv(path_buffer)# 
    df['Date Time'] = df['Date Time'].astype('str')
    df = df.append(df_ed)# ,ignore_index=True  # reindex
    df = df.drop_duplicates(subset=['Date Time'], keep='first')                    #去掉重复的行，并保留重复出现的行中第一次出现的行
    df.reset_index(drop=True, inplace=True)                  
    df.to_csv(path_buffer,index=False)

    return df    

# 周期变换
def transfer_to_period_data(df, rule_type='15T'):
    """
    将数据转换为其他周期的数据
    :param df:
    :param rule_type:
    :return:
    """
    df['Date Time'] = pd.to_datetime(df['Date Time']) # ,unit='ms'
    # =====转换为其他分钟数据
    period_df = df.resample(rule=rule_type, on='Date Time', label='left', closed='left').agg(
        {'Open': 'first',
         'High': 'max',
         'Low': 'min',
         'Close': 'last',
         'Volume': 'sum',
         })
    period_df.dropna(subset=['Open'], inplace=True)  # 去除一天都没有交易的周期
    period_df = period_df[period_df['Volume'] > 0]  # 去除成交量为0的交易周期
    period_df.reset_index(inplace=True)
    df = period_df[['Date Time', 'Open', 'High', 'Low', 'Close', 'Volume']]

    return df

# sleep
def next_run_time(time_interval, ahead_time=1):

    if time_interval.endswith('m'):
        now_time = datetime.now()
        time_interval = int(time_interval.strip('m'))

        target_min = (int(now_time.minute / time_interval) + 1) * time_interval
        if target_min < 60:
            target_time = now_time.replace(minute=target_min, second=0, microsecond=0)
        else:
            if now_time.hour == 23:
                target_time = now_time.replace(hour=0, minute=0, second=0, microsecond=0)
                target_time += timedelta(days=1)
            else:
                target_time = now_time.replace(hour=now_time.hour + 1, minute=0, second=0, microsecond=0)

        # sleep直到靠近目标时间之前
        if (target_time - datetime.now()).seconds < ahead_time+1:
            print('距离target_time不足', ahead_time, '秒，下下个周期再运行')
            target_time += timedelta(minutes=time_interval)
        # print('下次运行时间', target_time)
        return target_time
    else:
        exit('time_interval doesn\'t end with m')
        
        
def signal_bolling(df, para=[100, 2]):
    """
    布林线中轨：n天收盘价的移动平均线
    布林线上轨：n天收盘价的移动平均线 + m * n天收盘价的标准差
    布林线上轨：n天收盘价的移动平均线 - m * n天收盘价的标准差
    当收盘价由下向上穿过上轨的时候，做多；然后由上向下穿过下轨的时候，平仓。
    当收盘价由上向下穿过下轨的时候，做空；然后由下向上穿过上轨的时候，平仓。
    :param df:  原始数据
    :param para:  参数，[n, m]
    :return:
    """

    # ===计算指标
    n = para[0]
    m = para[1]

    # 计算均线
    df['median'] = df['Close'].rolling(n, min_periods=1).mean()

    # 计算上轨、下轨道
    df['std'] = df['Close'].rolling(n, min_periods=1).std(ddof=0)  # ddof代表标准差自由度
    df['upper'] = df['median'] + m * df['std']
    df['lower'] = df['median'] - m * df['std']

    # ===找出做多信号
    condition1 = df['Close'] > df['upper']  # 当前K线的收盘价 > 上轨
    condition2 = df['Close'].shift(1) <= df['upper'].shift(1)  # 之前K线的收盘价 <= 上轨
    df.loc[condition1 & condition2, 'signal_long'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多

    # ===找出做多平仓信号
    condition1 = df['Close'] < df['median']  # 当前K线的收盘价 < 中轨
    condition2 = df['Close'].shift(1) >= df['median'].shift(1)  # 之前K线的收盘价 >= 中轨
    df.loc[condition1 & condition2, 'signal_long'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    # ===找出做空信号
    condition1 = df['Close'] < df['lower']  # 当前K线的收盘价 < 下轨
    condition2 = df['Close'].shift(1) >= df['lower'].shift(1)  # 之前K线的收盘价 >= 下轨
    df.loc[condition1 & condition2, 'signal_short'] = -1  # 将产生做空信号的那根K线的signal设置为-1，-1代表做空

    # ===找出做空平仓信号
    condition1 = df['Close'] > df['median']  # 当前K线的收盘价 > 中轨
    condition2 = df['Close'].shift(1) <= df['median'].shift(1)  # 之前K线的收盘价 <= 中轨
    df.loc[condition1 & condition2, 'signal_short'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓
    # df.drop_duplicates(subset=['signal_long', 'signal_short'], inplace=True)   # 去除signal_long', 'signal_short 列重复值

    # ===合并做多做空信号，去除重复信号
    df['signal'] = df[['signal_long', 'signal_short']].sum(axis=1, skipna=None)         # 行向求和
    df.loc[df['signal_long'].isnull() & df['signal_short'].isnull(),'signal']=np.nan    # 条件赋值NAN
    
    
    # 筛选转向操作信号
    temp = df[df['signal'].notnull()][['signal']]           # signal列非空值
    temp = temp[temp['signal'] != temp['signal'].shift(1)]  # get 与上一行signal列值不同的行
    df['signal'] = temp['signal']   # 列赋值
    df.drop(['std', 'signal_long', 'signal_short'], axis=1, inplace=True)   # 删除计算过程列  'median', 'upper', 'lower', 

    # ===由signal计算出实际的每天持有仓位
    # signal的计算运用了收盘价，是每根K线收盘之后产生的信号，到第二根开盘的时候才买入，仓位才会改变。
    df['pos'] = df['signal'].shift()        # add column 'pos' = 上一行row 'signal'值
    df['pos'].fillna(method='ffill', inplace=True)      # column 'pos'空值同上不全
    df['pos'].fillna(value=0, inplace=True)  # 将初始行数的position补全为0

    return df


def signal_moving_average(df, para=[5, 60]):
    """
    简单的移动平均线策略
    当短期均线由下向上穿过长期均线的时候，买入；然后由上向下穿过的时候，卖出。
    :param df:  原始数据
    :param para:  参数，[ma_short, ma_long]
    :return:
    """

    # ===计算指标
    ma_short = para[0]
    ma_long = para[1]

    # 计算均线
    df['ma_short'] = df['Close'].rolling(ma_short, min_periods=1).mean()
    df['ma_long'] = df['Close'].rolling(ma_long, min_periods=1).mean()

    # ===找出买入信号
    condition1 = df['ma_short'] > df['ma_long']  # 短期均线 > 长期均线
    condition2 = df['ma_short'].shift(1) <= df['ma_long'].shift(1)  # 之前的短期均线 <= 长期均线
    df.loc[condition1 & condition2, 'signal'] = 1  # 将产生做多信号的那根K线的signal设置为1，1代表做多

    # ===找出卖出信号
    condition1 = df['ma_short'] < df['ma_long']  # 短期均线 < 长期均线
    condition2 = df['ma_short'].shift(1) >= df['ma_long'].shift(1)  # 之前的短期均线 >= 长期均线
    df.loc[condition1 & condition2, 'signal'] = 0  # 将产生平仓信号当天的signal设置为0，0代表平仓

    df.drop(['ma_short', 'ma_long'], axis=1, inplace=True)

    # ===由signal计算出实际的每天持有仓位
    # signal的计算运用了收盘价，是每根K线收盘之后产生的信号，到第二根开盘的时候才买入，仓位才会改变。
    df['pos'] = df['signal'].shift()
    df['pos'].fillna(method='ffill', inplace=True)
    df['pos'].fillna(value=0, inplace=True)  # 将初始行数的position补全为0

    return df        



def calculateEMA(period, closeArray, emaArray=[]):
    """计算指数移动平均"""
    length = len(closeArray)
    nanCounter = np.count_nonzero(np.isnan(closeArray))
    if not emaArray:
        emaArray.extend(np.tile([np.nan],(nanCounter + period - 1)))
        firstema = np.mean(closeArray[nanCounter:nanCounter + period - 1])    
        emaArray.append(firstema)    
        for i in range(nanCounter+period,length):
            ema=(2*closeArray[i]+(period-1)*emaArray[-1])/(period+1)
            emaArray.append(ema)        
    return np.array(emaArray)
    
def signal_MACD(closeArray,shortPeriod = 12 ,longPeriod = 26 ,signalPeriod =9):
    ema12 = calculateEMA(shortPeriod ,closeArray,[])
    ema26 = calculateEMA(longPeriod ,closeArray,[])
    diff = ema12-ema26
    
    dea= calculateEMA(signalPeriod ,diff,[])
    macd = 2*(diff-dea)
    return macd,diff,dea 





def close_position(symbol):
    print('doing close postion\t%s'% symbol)
    while True:
        try:
            d_position = accountAPI.get_positions('SWAP', symbol)
            if d_position['data'] != []:
                d_position = d_position['data'][0]          # get position
                sz = int(d_position['availPos'])      # 可平仓数量    单位：张  
                if sz > 0 :            # close-position
                    if d_position['posSide'] == 'long':         # have long position
                        price = float(marketAPI.get_ticker(symbol)['data'][0]['bidPx'])    # get bid 1
                        result = tradeAPI.place_order(instId=symbol, tdMode='cross', side='sell',posSide='long', ordType='limit', sz=sz, px=price)#sell long 平多
                        result = tradeAPI.get_orders(symbol, result['data'][0]['ordId'])
                        state = result['data'][0]['state']      # 成交状态
                        pnl = result['data'][0]['pnl']              # 成交收益
                        ordid = result['data'][0]['ordId']          # 订单号
                        log_write(file="log_strategy_okex.txt", content='%s\tclose long position\t%s: %s * %s\t%s\tpnl:%s\tid:%s' % (run_time.strftime('%Y-%m-%d %H:%M'),symbol, price,sz, state, pnl, ordid )) # write log
                        # result = tradeAPI.place_order(instId='BTT-USDT-SWAP', tdMode='cross', side='sell',posSide='long', ordType='limit', sz=50, px=0.012)
                    else:
                        price = float(marketAPI.get_ticker(symbol)['data'][0]['askPx'])    # get ask 1
                        result = tradeAPI.place_order(instId=symbol, tdMode='cross', side='buy',posSide='short', ordType='limit', sz=sz, px=price)# buy short 平空
                        result = tradeAPI.get_orders(symbol, result['data'][0]['ordId'])
                        state = result['data'][0]['state']      # 成交状态
                        pnl = result['data'][0]['pnl']              # 成交收益
                        ordid = result['data'][0]['ordId']          # 订单号
                        # print("tradeAPI.place_order(instId=symbol, tdMode='cross', side='buy',posSide='short', ordType='limit', sz=%s, px=%s)" % (sz, price))  # debug
                        log_write(file="log_strategy_okex.txt", content='%s\tclose short position\t%s: %s * %s\t%s\tpnl:%s\tid:%s' % (run_time.strftime('%Y-%m-%d %H:%M'),symbol, price,sz, state, pnl, ordid )) # write log
                        #print('close short position\t%s: %s * %s\t%s' % (symbol, price, sz, result['data'][0]['ordId'] ))       
            break
        except :   
            time.sleep( 1 )                    
                                                

def get_candle_from_okex(symbol='ltc_usdt', kline_type=15, after=0):
    time.sleep(0.1) #seconds
    while True:         # get new data                
        try:
            result = marketDataAPI.get_candlesticks(symbol, bar=kline_type, after = str(after))['data'] 
            if len(result):  # 当返回内容为空的时候，跳过本次循环# 整理dataframe
                return (result)
                #l_kl.extend(result)             #entr data
            else:      
                break      
            ##df = pd.DataFrame(result['data'], dtype='float', columns=['candle_begin_time','open', 'high','low','close','volume','vol_coin'])
            ##df = df.iloc[::-1]    # df rows reverse
            ##df.reset_index(drop=True, inplace=True)     # df index reset
            #break
        except :   
            time.sleep( 1 )

def get_list_from_okx(instType='SWAP'):
    symbols = marketDataAPI.get_tickers(instType=instType)           # 获取所有产品行情信息  Get Tickers
    symbols = pd.DataFrame(symbols, dtype='float')                 #dict to dataframe
    symbols = symbols.loc[symbols ['instId'].str.contains('-USDT'), ['instId','vol24h']]    #-USDT筛选列 行 _token  
    symbols = symbols.sort_values(["vol24h"],ascending=False)        #volume_24h排降序
    symbols = symbols['instId'].values.tolist()     # get [instrument_id]列
    return (symbols)

get_list_from_okx('SWAP')

def volume_burst(df, multiple=3): # 阶段放量
    condition = df['Volume'] >= df['Volume'].shift(1) * multiple  # 放量N倍 
    df.loc[condition, 'burst'] = 1  # 放量标记为 1
    # print(df[df['burst'] == 1] [['Date Time','Volume','burst']])
    return df 
def volume_grow(df):
    condition1 = df['Volume'] >= df['Volume'].shift(1)   # 连续放量 
    condition2 = df['Close'] >= df['Close'].shift(1)   # 连续放量 
    df['vol_grow'] = 0
    df.loc[condition1 & condition2 ,'vol_grow'] = 1 # 放量标记为 1
    df.loc[df['vol_grow'].shift(1) != 'NaN','vol_grow'] = df['vol_grow'].shift(1) + 1
    print(df[df['vol_grow'] == 1] [['Date Time','Volume','vol_grow']])
    return df


def low_high_std(l_symbols,period,amount):
    kline_type = '5m'
    df_kline
    for symbol in l_symbols:
        path_buffer = os.path.join('..','data', 'okex_' + symbol + '_' + kline_type + '.csv')
        path_buffer = os.path.join('..','data', 'okex_1INCH-USDT-SWAP_5m.csv')
        if os.path.exists(path_buffer) :# load data
            df = pd.read_csv(path_buffer)
            df = transfer_to_period_data(df, rule_type = period) # transfer_to_period
            df = WindOkexLib.volume_burst(df,multiple=3) # 阶段放量
            df = WindOkexLib.volume_grow(df)        # 连续放量 
            # df = ['candle_begin_time'] = pd.to_datetime(df['candle_begin_time'],unit='ms') + pd.Timedelta(hours=8)         # rename column
        else:
            print('No such file：\t%s' % path_buffer)                           # trade_amount
    return (l_std)

# ['Date Time','Open', 'High','Low','Close','Volume','Vol_coin']

def draw_curve_figure(df, name='symbol'):                     # 画图

    import matplotlib.pyplot as plt
    plt.figure(figsize=(18,10))#设置画布的尺寸
    plt.title(name,fontsize=20)#标题，并设定字号大小
    plt.xlabel(u'x-time',fontsize=14)#设置x轴，并设定字号大小
    plt.ylabel(u'y-equity',fontsize=14)#设置y轴，并设定字号大小

    #color：颜色，linewidth：线宽，linestyle：线条类型，label：图例，marker：数据点的类型
    plt.plot(df['Date Time'],df['equity_curve'],color="deeppink",linewidth=1,linestyle='-',label='equity', marker=None)
    name = name + '_equity.jpg'
    plt.savefig(name)
    return(plt)

#load data > updata ticker > calculate signal > trade
def back_test(df,signal='bolling'):
    #calculate Capital curve from pos
    df['change'] = df['Close'].pct_change(1)                                # close Up and down
    df['buy_at_open_change'] = df['Close'] / df['Open'] -1                  # Up and down of today
    df['sell_next_open_change'] = df['Open'].shift(-1) / df['Close'] -1        # 今天close-明天open的涨跌幅
    df.at[len(df) - 1, 'sell_next_open_change'] = 0                         # end value set 0
    #print('{}\n{}'.format(df.head(1),df.tail(1) ))

    #select time slot 
    #df = df[df['Date Time'] >= pd.to_datetime('2017-01-01')]        # 选取符合条件的数据
    #df.reset_index(drop=True, inplace= True)           # reset index
    # condition of open/close position
    condition1 = df['pos'] != 0
    condition2 = df['pos'] != df['pos'].shift(1)          # condition of open position
    open_pos_condition = condition1 & condition2

    condition1 = df['pos'] != 0
    condition2 = df['pos'] != df['pos'].shift(-1)          # condition of close position
    close_pos_condition = condition1 & condition2
    #grouping every trade      print('{}\n{}'.format(period_df.head(1),period_df.tail(1) ))
    df.loc[open_pos_condition,'start_time'] = df['Date Time']			#
    df['start_time'].fillna(method='ffill', inplace=True)				# NaN值up填充
    df.loc[df['pos'] == 0, 'start_time'] = pd.NaT                           # pos:0 > start_time:NaT
    # base parameters
    leverage_rate = 3   # 杠杆
    init_cash = 100     # 启动资金
    c_rate = 0.002        # 手续费
    # para = [20,200]     # Policy parameters
    min_margin_rate = 0.15      # 最低保证金比例 
    min_margin = init_cash * leverage_rate * min_margin_rate    # 最低保证金
    # claculate position change
    # 开仓时仓位
    df.loc[open_pos_condition,'position'] = init_cash * leverage_rate * (1 + df['buy_at_open_change'])
    # 开仓后每天的仓位变动
    group_num = len(df.groupby('start_time'))
    if group_num > 1:
        t = df.groupby('start_time').apply(lambda x: x['Close'] / x.iloc[0]['Close'] * x.iloc[0]['position'])
        t = t.reset_index(level=[0]) 
        df['position'] = t['Close']
    # 每根Kline仓位的最大值和最小值，针对最高价和最低价
    df['position_max'] = df['position'] * df['High'] / df['Close']
    df['position_min'] = df['position'] * df['Low'] / df['Close']
    # 平仓时仓位
    df.loc[close_pos_condition,'position'] *= (1 + df.loc[close_pos_condition,'sell_next_open_change'])
    # calculate 每天持有资金的变化
    df['profit'] = (df['position'] -init_cash * leverage_rate) * df['pos']              # calculate持仓利润
        # calculate 持仓利润最小值
    df.loc[df['pos'] == 1, 'profit_min'] = (df['position_min'] - init_cash * leverage_rate) * df['pos']  # 最小持仓利润
    df.loc[df['pos'] == -1, 'profit_min'] = (df['position_max'] - init_cash * leverage_rate) * df['pos']  # 最小持仓利润
    #print(df[['Date Time','pos','start_time','position','profit']])     

    # calculate 实际资金量

    df['cash'] = init_cash + df['profit']  # 实际资金

    df['cash'] -= init_cash * leverage_rate * c_rate                    # 减去建仓手续费                
    df['cash_min'] = df['cash'] - (df['profit'] - df['profit_min'])     # 实际最小资金    
    df.loc[close_pos_condition,'cash'] -= df.loc[close_pos_condition, 'position'] * c_rate   # 减去平仓时手续费
    # 是否有爆仓
    _index = df[df['cash_min'] <= min_margin ].index
    if len(_index) > 0:
        # print('Burst Position')
        df.loc[_index, '强平'] = 1
        df['强平'] = df.groupby('start_time')['强平'].fillna(method='ffill')
        df.loc[(df['强平'] == 1) & df['强平'].shift(1) != 1, 'cash_强平'] =df['cash_min']         # 有问题
        df.loc[(df['pos'] != 0) & df['强平'] == 1, 'cash'] = None
        df['cash'].fillna(value=df['cash_强平'], inplace=True)
        df['cash'] = df.groupby('start_time')['cash'].fillna(method='ffill')
        df.drop(['强平', 'cash_强平'], axis=1, inplace=True)      # 清理不必要数据
        return(0)
        # 97 计算资金曲线
    df['equity_change'] = df['cash'].pct_change()
    # print(df[['candle_begin_time','pos','position','cash','equity_change']])
    df.loc[open_pos_condition, 'equity_change'] = df.loc[open_pos_condition, 'cash'] / 100 -1  # 开仓日收益率
    df['equity_change'].fillna(value=0, inplace=True) 
    df['equity_curve'] = (1 + df['equity_change']).cumprod()
    # df.to_csv('debug.csv')
        # 清理过程数据
    df.drop(['change','buy_at_open_change','sell_next_open_change','start_time','position','position_max','position_min','profit','profit_min','cash','cash_min','equity_change' ], axis=1, inplace=True)
    #draw figure
    #plt = draw_curve_figure(df, name=symbol + '_' + period)
    #path_buffer = os.path.join('..','result', 'okex_' + symbol + '_' + symbol + '_' + period + '.jpg')
    #plt.savefig(path_buffer)
    #plt.legend(loc=2)#图例展示位置，数字代表第几象限
    #plt.show()#显示图像
    return(df.iloc[-1,-1])

def calculate_period_growth(symbol,df, period=30): #return(l_data)
    df = df.iloc[:-1,1:5] # 切片价格
    # symbol    Open    High     Low   15_grow   30_grow   60_grow   100_grow   360_grow
    l_data = [symbol, df.iloc[-1,1], df['High'].max(), df['Low'].min()]
    for x in period:
        if x < df.shape[0] :
            l_data.append(df.iloc[-x,3] / df.iloc[-1,1])
        else:
            l_data.append('-')
    return (l_data)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ccxt
import time
import pandas as pd
from urllib.request import urlopen,Request
import json
import numpy as np
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

"""
exchange = 'gate'  # 以gateio交易所为例
get_futures_funding_rate_csv(exchange)





pd.set_option('expand_frame_repr', False) #当列太多时不换行

def get_url_content(url, max_try_number=5):
    try_num = 0
    while True:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
            request = Request(url=url, headers=headers)
            content = urlopen(request, timeout=15).read()
            return content
        except Exception as http_err:
            print(url, "抓取报错", http_err)
            try_num += 1
            if try_num >= max_try_number:
                print("尝试失败次数过多，放弃尝试")
                return None


def get_list_symbols(exchang='huobi'):

    # 创建一个空的df
    df = pd.DataFrame()

    # 构建交易对url
    if exchang == 'huobi' :
        url = 'https://api.btcgateway.pro/api/v1/common/symbols'      #现货      /v1/contract_contract_info  合约
    elif exchang == 'okex' :
        url = 'https://www.okexcn.com/api/futures/v3/instruments'
    elif exchang == 'gateio' :
        url = 'https://data.gateapi.io/api2/1/pairs'
    else:
        print('Lack of exchanges')   

    content = get_url_content(url, 5)   # 联网
    # print(content)
    # print(type(content))

    # 转换格式
    # content = content.decode("utf-8")
    # print(type(content))
    json_data = json.loads(content.decode("utf-8"))
    if type(json_data) != 'list':
        pass
    else:
        json_data = json_data['data']
    symbol_list  = [s for s in json_data if '_USDT' in s]# get [json_data]包含_USDT的项
    # 排除不可交易对
    #url = 'https://data.gateapi.io/api2/1/coininfo'
    #content = get_url_content(url, 5)   # 联网
    #json_data = json.loads(content.decode("utf-8"))
    #json_data = json_data['coins']
    #for coin in json_data:              #总list
        #for key1 in coin:               #coin dict
            #for key2 in coin[key1]:     #coin state
                #if key2 == 1:
                    #symbol_list.pop(key1)
    #list(set(a).difference(set(b))) # list差集
    #print(json_data)
    #df_symbols = pd.DataFrame(json_data, dtype='str')
    # print(df)
    # print(type(df))

    # 取某几列
    #df = df[['base-currency', 'quote-currency', 'symbol-partition']]

    # 新增一列
    #df['base-quote'] = df['base-currency'] + df['quote-currency']
    #df['resource'] = 'huobi'

    ## 对df进行整理
    #df = df[['base-currency','quote-currency','base-quote','symbol-partition','resource']]

    #symbol_list = list(df['base-quote'])
    # 存储数据
    # df.to_csv('symbols.csv', index=False)

    return symbol_list



# 获取k线数据
#def get_candle_from_huobi(period='1day',size=1):
    #symbol_list = get_list_symbols(exchang)


    ## 创建一个空的df
    #df = pd.DataFrame()

    ## 遍历每一个symbol
    #for symbol in symbol_list[:20]:
        #print(symbol)
        ## 构建url
        #url = 'https://api.huobipro.com/market/history/kline?period=%s&size=%s&symbol=%s' % (period,size,symbol)
        ## print(url)
        ## exit()
        ## 抓取数据
        ## headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        ## request = Request(url=url, headers=headers)
        #content = get_url_content(url)

        #if content is None:
            #continue
        ## print(content)
        ## print(type(content))
        ## exit()
        ## 将数据转换成df
        #json_data = json.loads(content.decode("utf-8"))

        ## print(json_data['data'])
        ## exit()
        #_df = pd.DataFrame(json_data['data'], dtype='float')
        ## _df = _df.T#.T 矩阵转秩
        ## print(_df)
        #_df['symbol'] = symbol
        ## print(_df)
        #df = df.append(_df,ignore_index=0)
        ## print(df)
        ##exit()
    ## 对df进行整理
    #df = df[['symbol','id','high','low','open','close','vol']]
    ## print(df)
    ## 重命名
    #df.rename(columns={'id':'time'},inplace=True)
    ## print(df)
    #df['time'] = pd.to_datetime(df['time'],unit='s') + pd.Timedelta(hours=8)

    #return df


#df = get_candle_from_huobi(period='1day', size=1)

#
 
 
def get_candles(symbol, n_kline, n_hours):
    #url = 'https://data.gateapi.io/api2/1/candlestick2/btc_usdt?group_sec=86400&range_hour=26280'
    url = 'https://data.gateapi.io/api2/1/candlestick2/{}?group_sec={}&range_hour={}'.format(symbol.lower(), n_kline,n_hours)
    content = get_url_content(url, 5)   # 联网
    # 转换格式
    # content = content.decode("utf-8")
    json_data = json.loads(content.decode("utf-8"))
    json_data = json_data['data']
    if json_data:
    #else:
        #json_data = json_data['data']
        df_candles = pd.DataFrame(json_data)
        df_candles.rename(columns={0: 'MTS', 1: 'volume', 2: 'close', 3: 'high', 4: 'low', 5: 'open'}, inplace=True)
        df_candles['MTS'] = pd
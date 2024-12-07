#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ccxt
import pandas as pd
import time
import asyncio                      #支持异步调用
import ccxt.async_support as ccxt   #支持异步调用ccxt
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option("display.max_rows", 500)
import os
import wind_library

 
# 从ccxt获取K线数据创建okex交易所
def ccxt_get_kline(exchange,Transaction_type,kline_period):
    # exchange = ccxt.gate () # default id
    # id = exchange     # 设置id为'gate'
    btcchina = eval ('ccxt.%s ()' % exchange)     # 使用eval函数动态创建参数指定的交易所实例
    gdax = getattr (ccxt, 'okx') ()        # 使用getattr函数获取gate交易所实例

    # from variable id          # 从变量id获取交易所
    exchange_id = 'okx'
    exchange_class = getattr(ccxt, exchange)     # 通过getattr函数获取交易所类
    exchange = exchange_class({     # 创建交易所实例
        'apiKey': 'YOUR_API_KEY',
        'secret': 'YOUR_SECRET',
        'timeout': 30000,
        'enableRateLimit': True,
    })
    #print (dir (ccxt.okex ()))                  #get 交易所实例的所有方法
    markets = exchange.load_markets()           #get 交易品种    
    #print(markets)
    #get K line
    df_kl = pd.DataFrame()    #空表初始化columns=['DataTime','open', 'High','Low','Close','volume']
    l_kl =[]
    for symbol in exchange.markets:         #get 现货交易品种%
        if '/USDT' in symbol:               #筛选USDT交易对
            print(symbol )
            #t_since = int(time.time() * 1000)              #z最后kline时间
            #limit = 200                              #数量限制
            #get kline
            if exchange.has['fetchOHLCV']:        # 早于当前时间
                time.sleep (exchange.rateLimit / 5000) # time.sleep wants seconds
                kline_type = '4h' 
                kldata = exchange.fetch_ohlcv(symbol, timeframe=kline_type) #, since=t_since, limit=None, params={})
                #kldata = exchange.fetch_ohlcv (symbol, '1d',since = t_since) # one day   ?since 
                #print(kldata[0])   debug
                if kldata :              #如果有数据
                    df_kl = pd.DataFrame(kldata, columns=['datatime','open', 'high','low','close','volume'])    #创建列名称'DataTime','open', 'High','Low','Close','volume'
                    df_kl['DataTime'] = pd.to_datetime(df_kl['DataTime'], unit='ms')        #时间格式化
                    #print('{}:{}'.format(t_since,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t_since / 1000) )))  # ISO时间格式化
                    print('{}\n{}\n{}'.format(df_kl.shape,df_kl.head(1),df_kl.tail(1) ))    #屏幕打印表格首尾行
    return(df_kl)

ccxt_get_kline('gate','swap','1d')            
            
        #     print('leng of table =' + str(len(kldata)))
        # #写入文件
        # df_kl.to_csv(os.path.join('..','data',exchange_id + '_' + symbol.replace('/','_') + '_' + kline_type + '.csv'),index=False)
'''
        
        


print(df_kl)

exit()
#secretkey = "C6938CE7550AE3413AEBC27BEE9264E7"
#password="这里根据申请api时的内容填写"



if (exchange.has['fetchTicker']):           #get 实时行情
    print(exchange.fetch_ticker('LTC/USDT')) # ticker for LTC/ZEC

#由于现在直接访问okex会被墙，需要通过代理的方式访问，若是国外服务器则不需要下面的这几行代码
#okex.proxies={
    #'http': 'socks5://127.0.0.1:10808',
    #'https': 'socks5://127.0.0.1:10808',
#}

#get OrderBook Data
#delay = 1 #seconds
#for symbol in exchange.markets:
    #print(exchange.fetch_order_book(symbol))
    #time.sleep(delay)       #rate limit



df = pd.DataFrame(exchange.markets).T
# 获取所有交易所品种
def get_symbols_all_exchanges():
    list_exchangs = ccxt.exchanges #get all exchanges
    list_symbols = []
    # 创建DataFrame，变量rows作为表的行名，变量columns作为表的列名。
    df = pd.DataFrame( columns=list_exchangs)
    for exchang in list_exchangs:
        list_symbols = list_symbols.append(markets = exchange.load_markets())           #get 交易品种 
        for symbol in list_symbols:
            #判定df表中的index是否存在与变量symbol等值的项，如果存在则在df表中的symbol值行exchang值列写入数值1，如果不存在则在df表中的symbol值行exchang值列写入数值0。
            
        # list_symbols = unique_sort_list(list_symbols)       #列表去重排序处理
    # df.at['ADF', 'Low'] = 1
    return(list_symbols)
# 找到有期货的交易所
#df = df[df['future']]
future_symbol_list = list(df.index)     #市场交易对

while True:
    print('*' * 10)
    # 遍历获取tick数据
    for future_symbol in future_symbol_list:
        if future_symbol not in ['EOS/USDT', 'BCH/USD']:
            continue

        print(future_symbol)
        symbol = future_symbol.replace('USDT', 'USDT')

        # 获取现货数据
        content = exchange.fetchTicker(symbol)
        del content['info']                     #del info dict
        df = pd.DataFrame([content])[['timestamp', 'datetime', 'bid', 'ask']]   #提取对应键值

        # 获取期货数据
        # for contract_type in ['this_week', 'next_week', 'quarter']:
        for contract_type in ['quarter']:
            content = exchange.fetchTicker(future_symbol, {'contract_type': contract_type})
            temp = pd.DataFrame([content])[['timestamp', 'datetime', 'bid', 'ask']]
            # 合并数据
            df = pd.merge(left=df, right=temp, left_index=True, right_index=True, suffixes=['', '_' + contract_type])

            #df['revenue_'+contract_type] = df['bid_'+contract_type] / df['ask'] - 1

        # 整理数据
        df['symbol'] = future_symbol
        df = df[['symbol'] + sorted(df.columns)]

        print(df)
        time.sleep(exchange.rateLimit / 1000)

    time.sleep(120)

'''

import os
import json
import ccxt
import pandas as pd
import pdb
 
# 循环获取指定交易所、指定参数的所有 USTD 交易对 k 线数据
def ccxt_save_kline(exchange, transaction_type='spot', kline_period='1d'):
    # transaction_type= Margin:杠杆	Swap:永续	Future:期货
    try:
        # 设置交易所
        exchange = getattr(ccxt, exchange)()
        # 加载市场信息
        markets = exchange.load_markets()
        # 获取所有 USDT 指定类型的交易对
        usdt_perpetual_markets = [market for market in markets if exchange.markets[market]['type'] == transaction_type and market.endswith('USDT')]
        # 循环获取所有符合要求的交易对
        for symbol in usdt_perpetual_markets:
            print(f'{symbol} : {exchange.markets[symbol][transaction_type]}')
            if exchange.markets[symbol][transaction_type]:
                klines = exchange.fetch_ohlcv(symbol, kline_period)
                if klines:
                    df_kl = pd.DataFrame(klines, columns=['datatime', 'open', 'high', 'low', 'close', 'volume'])
                    df_kl['datatime'] = pd.to_datetime(df_kl['datatime'], unit='ms')
                    print('{}\n{}\n{}'.format(df_kl.shape, df_kl.head(1), df_kl.tail(1)))
                    filename = os.path.join('..', 'data', f'{exchange}_{exchange.markets[symbol]['base']}_{transaction_type}_{kline_period}.csv')
                    df_kl.to_csv(filename, index=False)
                    print(f' save: {filename} finish' )
                    #pdb.set_trace()   #jupyter notebook debug
    except Exception as e:
        print(f"发生错误：{e}")

# example:  ccxt_save_kline('gate')#, 'swap', '15m'



    #list去重复项并按数字小到大，字母a-z重新排序
def unique_sort_list(input_list):
    # 去重复项
    unique_list = list(set(input_list))
    # 按数字小到大排序
    unique_list.sort(key=lambda x: (isinstance(x, int), x) if isinstance(x, (int, float)) else (False, x))
    # 按字母a-z重新排序
    unique_list.sort(key=lambda x: (isinstance(x, str), x.lower()) if isinstance(x, str) else (False, x))
    return unique_list
import ccxt
import pandas as pd
import os

def get_symbols_all_exchanges():
    # 获取所有交易所列表
    list_exchanges = ccxt.exchanges
    list_symbols = []
    # 创建一个空的DataFrame，列名为所有交易所
    df = pd.DataFrame(columns=list_exchanges)

    # 遍历每个交易所
    for exchange_id in list_exchanges:
        print('正在获取交易所信息---'+ exchange_id)
        try:
            # 创建交易所对象
            exchange = getattr(ccxt, exchange_id)()
            # 获取该交易所支持的交易品种
            markets = exchange.load_markets()
            symbols = list(markets.keys())
            list_symbols.extend(symbols)

            # 遍历每个交易品种
            for symbol in symbols:
                # 筛选出包含'/USDT'的交易对
                if '/USDT' in symbol:
                    # 如果交易对不在DataFrame的索引中，则添加一行并初始化为0
                    if symbol not in df.index:
                        df.loc[symbol] = 0
                    # 将支持该交易对的交易所在DataFrame中标记为1
                    df.loc[symbol, exchange_id] = 1

        except Exception as e:
            # 捕获异常并输出错误信息
            print(f"Failed to connect to or access data from exchange: {exchange_id}. Error: {e}. Skipping...")
            continue

    # 计算每一行的数值总和
    df['Sum'] = df.sum(axis=1)
    
    return df

# 调用函数获取所有交易所支持的交易品种信息
symbols_df = get_symbols_all_exchanges()
# 打印DataFrame
print(symbols_df)
symbols_df.to_csv(os.path.join('..','data','all_symbols' + '.csv'),index=True)  #表格写入csv文件
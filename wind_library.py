# -*- coding: utf-8 -*-
import os
import re 
import sys
import pdb
import json
import ccxt
import nbformat
import pandas as pd
from tqdm import tqdm
import pandas_ta as ta  
import matplotlib.pyplot as plt

# 获取K线,返回dataframe['datetime', 'open', 'high', 'low', 'close', 'volume']
def get_ccxt_exchange_kline(exchange, symbol, transaction_type='spot', kline_period='1d', limit=None):
    """
    获取指定交易所指定币对的k线数据
    
    Args:
        exchange (str): 交易所名称
        symbol (str): 交易对
        transaction_type (str, optional): 交易类型, 可选值为'spot', 'margin', 'swap', 'future'. 默认为'spot'
        kline_period (str, optional): K线周期, 可选值为'1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M'. 默认为'1d'
        limit (int, optional): 获取的K线数量, 默认为None, 表示获取全部
    
    Returns:
        pandas.DataFrame: 包含K线数据的DataFrame
    """
    try:
        # 设置交易所
        exchange = getattr(ccxt, exchange)()
        
        # 获取K线数据
        klines = exchange.fetch_ohlcv(symbol, kline_period, limit=limit)
        
        # 转换为DataFrame
        df_kl = pd.DataFrame(klines, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df_kl['datetime'] = pd.to_datetime(df_kl['datetime'], unit='ms')
        df_kl.name = symbol
        
        return df_kl
    
    except Exception as e:
        print(f"发生错误：{e}")
        return None
# df = get_ccxt_exchange_kline('gate', 'BTC/USDT', 'spot', '1d', 100)


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
                    df_kl = pd.DataFrame(klines, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
                    df_kl['datetime'] = pd.to_datetime(df_kl['datetime'], unit='ms')
                    print('{}\n{}\n{}'.format(df_kl.shape, df_kl.head(1), df_kl.tail(1)))
                    filename = os.path.join('..', 'data', f'{exchange}_{exchange.markets[symbol]["base"]}_{transaction_type}_{kline_period}.csv')
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

'''
# task1: 写一个合并多个文件的文本内容到一个文件的python功能函数
函数名：Merge_into_one_file, 参数(path, filetype, newfilename)
新文件的格式："# " + 原文件名称 + "：" 占一行，然后是对应的文本内容，再插入一空行间隔。以此类推
保存到原路径。
如果filetype='ipynb'则只提取.ipynb文件cell里面的内容。
要求回复前自行举例试运行验证代码，如果有报错请解除到无报错再回复最终答案。
'''
import os
import nbformat

def Merge_into_one_file(path, filetype, newfilename, Subfolder=False):
    with open(os.path.join(path, newfilename), 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(filetype):
                    file_path = os.path.join(root, file)
                    if filetype == 'ipynb':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            notebook = nbformat.read(f, as_version=4)
                        for cell in notebook.cells:
                            if cell.cell_type == 'code':
                                outfile.write("# " + os.path.relpath(file_path, path) + ":\n")
                                outfile.write(cell.source)
                                outfile.write("\n\n")
                    else:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write("# " + os.path.relpath(file_path, path) + ":\n")
                            outfile.write(infile.read())
                            outfile.write("\n\n")
            if not Subfolder:
                break

# 示例用法
# Merge_into_one_file("D:\\document\\python\\QuantitativeTrading\\ccxt\\example_py", "ipynb", "ccxt_example_ipynb.txt", Subfolder=True)
# Merge_into_one_file("D:\\document\\python\\QuantitativeTrading\\vectorbt-master", "py", "vectorbr_Source code.txt", Subfolder=True)

# 金融绘图
def finance_plot(df, list_Ignored_columns):
    num_cols = len(df.columns) - len(list_Ignored_columns)
    fig, axs = plt.subplots(num_cols, 1, figsize=(10, 8*num_cols))
    subplots = {}
    
    for i, col in enumerate(df.columns):
        if col not in list_Ignored_columns:
            if col.startswith("ROC"):
                prefix = col.split("_")[0]
                if prefix not in subplots:
                    subplots[prefix] = axs[i-4]
                ax = subplots[prefix]
            else:
                ax = axs[i-4]
            
            ax.plot( df[col], color='blue', linewidth=1)
            ax.set_title(col)
            ax.grid(True)
    
    plt.tight_layout()
    plt.show()
# 示例调用动态绘图函数
# finance_plot(df, ['datetime', 'open', 'high', 'low'])  #dataframe, 不绘图的列名。

# 返回自然增长率，最大跌幅，最大涨幅
def close_max_multiple(df_kl):
    initial_close = df_kl['close'].iloc[0]
    last_close = df_kl['close'].iloc[-1]
    max_close = df_kl['close'].max()
    min_close = df_kl['close'].min()
    
    natural_growth = last_close / initial_close
    top_multiple = last_close / max_close
    down_multiple = last_close / min_close
    
    return natural_growth, top_multiple, down_multiple

# 生成器：获取指定交易所的k线数据；
def generator_ccxt_exchange_kline(exchange, transaction_type='spot', kline_period='1d', limit = None):
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
            # print(f'{symbol} : {exchange.markets[symbol][transaction_type]}')
            if exchange.markets[symbol][transaction_type]:
                klines = exchange.fetch_ohlcv(symbol, kline_period, limit = limit) # get Kline
                if klines:
                    df_kl = pd.DataFrame(klines, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
                    df_kl['datetime'] = pd.to_datetime(df_kl['datetime'], unit='ms')
                    df_kl.name = symbol  # 命名
                    yield df_kl
    except Exception as e:
        print(f"发生错误：{e}")
# 调用函数
# gen = generator_ccxt_exchange_kline('gate', 'swap')

# 生成金叉死叉函数
# 金叉:1，死叉:-1，不操作:0
def cross_up_and_down(df, column_name1, column_name2):
    """
    生成金叉死叉信号

    Parameters:
    df (pandas.DataFrame): 包含需要进行交叉判断的数据的DataFrame。
    column_name1 (str): 第一个列名，用于判断金叉的指标。
    column_name2 (str): 第二个列名，用于判断金叉的指标。

    Returns:
    pandas.Series: 包含金叉死叉信号的Series。
    """

    # 判断传入的列名是否存在于DataFrame中
    if column_name1 not in df.columns or column_name2 not in df.columns:
        raise ValueError("指定的列名不存在于DataFrame中")

    # 计算金叉和死叉信号
    signals = ta.cross(df[column_name1], df[column_name2]) # 金叉信号
    cross_signal = ta.cross(df[column_name2], df[column_name1])         # 死叉信号       
    signals.loc[cross_signal[cross_signal == 1].index] = -1        # 合并死叉 赋值 -1

    return signals
# example
# df['signal_sma_close'] = cross_up_and_down(df, 'column_name1', 'column_name2')


# 返回以字符'signal'为前缀的列名的所有列末5行总和
def sum_last_5_rows(df):
    signal_columns = [col for col in df.columns if col.startswith('signal')]
    last_5_rows = df.tail(5)
    sum_last_5_rows = last_5_rows[signal_columns].sum()
    return sum_last_5_rows

#  震荡指标上下值交易信号生成函数
def value_down_and_up(df, column_name, down, up):
    signals = [0] * len(df)  # 初始化信号序列为0
    signal_generated = {'up': False, 'down': False}

    for i in range(len(df)):
        value = df[column_name].iloc[i]

        if not signal_generated['up'] and value > up:
            signals[i] = -1  # 指标首次大于up时，卖出信号标记-1
            signal_generated['up'] = True
        elif not signal_generated['down'] and value < down:
            signals[i] = 1  # 指标首次小于down时，买入信号标记1
            signal_generated['down'] = True

    return signals

# 示例用法
# df = value_down_and_up(df, 'RSI_14', 'RSI', 30, 70)


def ccxt_customize_exchange(exchange):
    exchange_instance = getattr(ccxt, exchange)()    #按参数创建交易所对象
    if exchange == 'okx':
        hostname = 'aws.okx.com'
    elif exchange == 'binance':
        hostname = 'htx.com.ve'
    elif exchange == 'htx':
        hostname = 'htx.com.ve'
    else:
        hostname = exchange_instance.hostname

    customize_urls = {
        'urls': {
            'api': {
                'public': 'https://' + hostname + '/',
                'private': 'https://' + hostname + '/',
            },
            'www': 'https://' + hostname + '/',
            'doc': 'https://' + hostname + '/docs-v5/zh/',
        },
        
        'hostname': hostname,
        'apiKey': 'YOUR_API_KEY',
        'secret': 'YOUR_API_SECRET',
    }

    # 将交易所对象的 urls 属性修改为 customize_urls 中的内容
    exchange_instance.urls = customize_urls['urls']
    exchange_instance.hostname = hostname
    return exchange_instance
# example
# exchange = ccxt_customize_exchange('okx')


# 列出指定交易所x天数内上市的指定类型的交易对。
def ccxt_list_symbols_of_exchange_indays(exchange_id, transaction_type='spot', days=15):
    # 初始化交易所
    try:
        # 设置交易所
        exchange = getattr(ccxt, exchange_id)()
        # 加载市场信息
        markets = exchange.load_markets()
        symbols = []
        past_time = exchange.seconds() - days * 24 * 60 * 60    # 计算过去x天的时间戳（单位：秒）
        # 获取所有 USDT 指定类型的交易对
        usdt_perpetual_markets = [market for market in markets if exchange.markets[market]['type'] == transaction_type and market.endswith('USDT')]
        # 循环获取所有符合要求的交易对
        for symbol in usdt_perpetual_markets:
            kline_length = len(exchange.fetch_ohlcv(symbol, '1d'))  # 获取日K线数据长度
            if kline_length <= days:
                symbols.append(symbol)

    except Exception as e:
        print(f"发生错误：{e}")

    return symbols
# 调用示例
# list_symbols = ccxt_list_symbols_of_exchange_indays('gate', 'swap', 10)   #spot

def pandasta_signals(df):
    roc_length= 12; MAROC_length=6; macd_fast= 12; macd_slow= 26; macd_signal=9 ;rst_length=14   # Parameter set
    
    df['volume_times'] = (df['volume'] / df['volume'].shift(1)).round(1)   # 计算当期成交量与上期成交量的比值
    has_value_greater_than_3 = any(df['volume_times'].tail(5) > 3)  # 判断末5行数据中是否有数值大于3
    count_greater_than_3 = (df['volume_times'].tail(5) > 3).sum()   # 统计末5行数据中大于3的数值个数
    # difine momentum Strategy
    momentumStrategy = ta.Strategy(
        name="Customizemomentum",
        description="roc, obv",
        ta=[
            {"kind": "roc", "length": 12}
            ,{"kind": "obv" }
            ,{"kind": "kdj"}
            ,{"kind": "rsi"}
            ,{"kind": "macd"}
            ,{"kind": "bbands"}
        ]
    )
    # 定义均线策略  
    sma_strategy = ta.Strategy(
        name="sma_strategy",
        description="sma, obv",
        ta=[
            {"kind": "sma", "length": 7}
            ,{"kind": "sma", "length": 26 }
            ,{"kind": "sma", 'close':'ROC_12', "length": MAROC_length, "prefix": "ROC"}
            ,{"kind": "sma", 'close':'OBV', "length": 7, "prefix": "OBV"}
            # ,{"kind": "sma"}
            ,{"kind": "sma", "close": "volume", "length": 20, "prefix": "VOLUME"}
        ]
    )
    # 定义趋势策略  
    trend_strategy = ta.Strategy(
        name="trend_strategy",
        description="increasing, obv",
        ta=[
            {"kind": "increasing", "close": "ROC_SMA_"+str(MAROC_length), "prefix": "ROC"}   #上升趋势
            # ,{"kind": "slope", "close": "volume", "prefix": "VOLUME", "to_degrees" :True}   # , "as_angle"=True
            ,{"kind": "above_value", "close": "ROC_SMA_"+str(MAROC_length), "value": 0, "asint":  True}  # 在o轴以下
            ,{"kind": "above_value", "close": "K_9_3", "value": 80, "asint":  True}     # KDJ 超买范围
            ,{"kind": "above_value", "close": "D_9_3", "value": 80, "asint":  True}
            ,{"kind": "below_value", "close": "K_9_3", "value": 20, "asint":  True}
            ,{"kind": "below_value", "close": "D_9_3", "value": 20, "asint":  True}     # KDJ 超卖范围
        ]
    )
    df.ta.strategy(momentumStrategy)  
    df.ta.strategy(sma_strategy)
    df.ta.strategy(trend_strategy)
        # 计算交易信号
    df['signal_sma_close'] = cross_up_and_down(df, 'SMA_7', 'SMA_26')   # SMA signal
    df['signal_sma_obv'] = cross_up_and_down(df, 'OBV', 'OBV_SMA_7')   # OBV SMA signal
    df['signal_sma_roc'] = cross_up_and_down(df, 'ROC_12', 'ROC_SMA_6')   # ROC SMA signal
    df['signal_ka_value'] =  df["K_9_3_A_80"].diff().fillna(0).astype(int).clip(0, 1).replace(1, -1)   #构造超买信号K
    df['signal_da_value'] =  df["K_9_3_A_80"].diff().fillna(0).astype(int).clip(0, 1).replace(1, -1)   #构造超买信号D
    df['signal_kb_value'] =  df["K_9_3_B_20"].diff().fillna(0).astype(int).clip(0, 1)    #构造超卖信号K
    df['signal_db_value'] =  df["K_9_3_B_20"].diff().fillna(0).astype(int).clip(0, 1)    #构造超卖信号D
    df['signal_sma_kd'] = cross_up_and_down(df, 'K_9_3', 'D_9_3')   # KD SMA signal
    df['signal_value_rsi'] = value_down_and_up(df, 'RSI_14', 30, 70)   # RSI 超买超买信号
    df['signal_MACDh'] = value_macd(df['MACDh_12_26_9'])
    df['signal_bbands'] = signal_bbands(df, 'BBL_5_2.0', 'BBU_5_2.0')
    return(df)
# example
# signals = pandasta_signals(df)

# MACD 柱线交易信号
def value_macd(macdh_series):
    signals = [0] * len(macdh_series)  # 初始化信号序列为0

    for i in range(1, len(macdh_series)):
        prev_value = macdh_series.iloc[i - 1]
        current_value = macdh_series.iloc[i]

        if prev_value < 0 and current_value > 0:
            signals[i] = 1  # 柱线从负值变为正值，产生买入信号
        elif prev_value > 0 and current_value < 0:
            signals[i] = -1  # 柱线从正值变为负值，产生卖出信号

    return signals
# example
# df['signal_MACDh'] = value_macd(df['MACDh_12_26_9'])


def signal_bbands(df, lower_band_col, upper_band_col):
    """
    生成布林带交易信号
    
    参数:
    df (pandas.DataFrame): 包含价格和布林带数据的DataFrame
    lower_band_col (str): 下轨线列名
    upper_band_col (str): 上轨线列名
    
    返回:
    pandas.Series: 交易信号序列
    """
    signal = pd.Series(0, index=df.index, dtype=int)# 新列置0
    
    # 当价格首次跌破下轨时卖出信号
    signal[(df['close'] < df[lower_band_col]) & (signal.shift(1) >= 0)] = -1
    
    # 当价格首次突破上轨时买入信号
    signal[(df['close'] > df[upper_band_col]) & (signal.shift(1) <= 0)] = 1
    
    return signal
# example
# df['signal_bbands'] = signal_bbands(df, 'BBL_5_2.0', 'BBU_5_2.0')


import os
import re      
import pdb
import requests
from lxml import etree
import time
import cssselect
import pandas as pd


# 金额格式“6.66万”转换为纯数字格式
def process_money_string(money_str):
    # 1. 移除"$"
    money_str = money_str.replace("$", "")
    
    # 2. 检查是否包含数字
    if not bool(re.search(r'\d', money_str)):
        return 0
    
    # 3. 把数字后面的"亿"、"万"或"万亿"单位移除后用精确到个位的数字表达原来的金额
    if "万亿" in money_str:
        # 如果包含"万亿"
        num, unit = money_str.split("万亿")
        num = float(num)
        result = num * 10000000000000
    elif "亿" in money_str:
        # 如果包含"亿"
        num, unit = money_str.split("亿")
        num = float(num)
        result = num * 100000000
    elif "万" in money_str:
        # 如果包含"万"
        num, unit = money_str.split("万")
        num = float(num)
        result = num * 10000
    else:
        # 如果不包含"亿"、"万"和"万亿"
        result = float(money_str)
    
    # 返回数字结果
    return int(result)


# 获取gate单币种信息
def get_gate_cryptocurrency_info(info_url):
    try:
        response = requests.get(info_url)
        if response.status_code == 200:
            html = response.text
            tree = etree.HTML(html)
            # 在这里编写爬取单个加密货币信息的代码
            sysbol = tree.xpath('//*[@id="__next"]/div[2]/div/div[2]/div/div/section[1]/div/div[1]/div[1]/div/div/div[1]/h1[2]/text()')[1]
            ranking = tree.xpath('//*[@id="__next"]/div[2]/div/div[2]/div/div/section[1]/div/div[1]/div[1]/div/div/div[2]/div/span/text()')[0].split('#')[1]
            market_value = tree.xpath('//*[@id="__next"]/div[2]/div/div[2]/div/div/section[2]/div/div/div[4]/div/div/text()')[0]
            print(sysbol)
            market_value = process_money_string(market_value)
            circulation_rate = tree.xpath('//*[@id="__next"]/div[2]/div/div[2]/div/div/section[2]/div/div/div[6]/div/div/text()')
            if circulation_rate: circulation_rate = circulation_rate[0].replace('%', '')
            describe = tree.cssselect("div.sc-38dc6162-3.hRbPmN")[0].text
            website = tree.xpath('//*[@id="__next"]/div[2]/div/div[2]/div/aside/section[1]/table/tr[2]/td/div/a/@href')
            # 并将信息以列表的形式返回
            list_info = [sysbol, ranking, market_value, circulation_rate, describe, website]
            return list_info
        else:
            print(f"访问网址 {info_url} 失败,状态码: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"访问网址 {info_url} 时出现异常: {e}")
        return None


    # 获取指定库的所有函数名
def save_package_help(package_name):
    """保存指定库的帮助文本到 .txt 文件"""
    package = __import__(package_name)
    all_functions = [func for func in dir(package) if callable(getattr(package, func))]

    # 创建一个 io.StringIO 对象，用于捕获 help 输出
    help_output = io.StringIO()

    # 重定向标准输出到 help_output
    sys.stdout = help_output

    # 遍历所有函数，获取帮助文本
    help_text = ""
    for func_name in all_functions:
        try:
            help_text += f"# {func_name}\n\n"  # 在每个函数帮助文本前插入标题
            help(getattr(package, func_name))
            help_text += help_output.getvalue() + "\n\n"  # 将帮助文本添加到总的帮助文本中
            help_output.truncate(0)  # 清空 help_output
            help_output.seek(0)
        except:
            pass

    # 恢复标准输出
    sys.stdout = sys.__stdout__

    # 将帮助文本保存为 .txt 格式的文件
    file_path = f"{package_name}_help.txt"
    with io.open(file_path, "w", encoding="utf-8") as file:
        file.write(help_text)

    print(f"帮助文本已保存到 {file_path}")

# example 调用函数保存指定库的帮助文本
# save_package_help("vectorbt")
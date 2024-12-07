# pandas-ta 的 ta.Strategy 的简单示例，该示例基于简单的移动平均线交叉策略
import pdb
import pandas as pd  
import pandas_ta as ta  
import wind_library
import matplotlib.pyplot as plt





if __name__ == '__main__':
    gen = wind_library.generator_ccxt_exchange_kline(exchange='gate', transaction_type='swap', kline_period='1d')  # spot # download Kline
    for df_kl in gen:
    # df = pd.read_csv('..//data//Gate.io_ACA_swap_1d.csv',index_col=0,parse_dates=True)  # 表格列名：datetime,open,hight,low,volume
        df = wind_library.pandasta_signals(df_kl)
        sum_signals = wind_library.sum_last_5_rows(df)   # 信号汇总
        print(df.tail(5)[[col for col in df.columns if col.startswith('signal')]].to_string(index=False, header=False))  # 输出信号列末5行
    # print(len(df.columns),  df.columns)   # 输出列数，列名
    # number = df['golden_cross'].sum()   #列值累计
    # indexes = df.index[df['golden_cross'] == 1].tolist()    #列中值为 1 的行号
    # print(','.join(map(str, df['golden_cross'])))   #列值连续输出
    
    #以下为绘图模块
    #  print(','.join(map(str, cross_points)))   cross_points.sum()
    # str_column_name = '_'.join(df[['close', 'SMA_7', 'SMA_26']].columns)  #拼接列名字符串
    ind_size = (18, 5) # 设置图形的宽度为 10，高度为 6
    df[['close', 'SMA_7', 'SMA_26']].tail(300).plot(figsize=ind_size, title='_'.join(df[['close', 'SMA_7', 'SMA_26']].columns))   #绘制价格移动平均线
    plt.show()
    df_fragment= df[['ROC_12','ROC_SMA_'+str(MAROC_length)]]
    df_fragment.tail(300).plot(figsize=ind_size, title='_'.join(df_fragment.columns))   #绘制ROC移动平均线
    plt.axhline(0, color='r', linestyle='--')  # 添加0横轴线
    plt.show()
    df[['OBV','OBV_SMA_7']].plot(figsize=(20, 6), title='OBV_SMA_7')
    plt.show()
    
    pdb.set_trace()
    df.ta.log_return(cumulative=True, append=True)
    df.ta.percent_return(cumulative=True, append=True)  
    # 添加简单移动平均线到 DataFrame  
    df['SMA_short'] = ta.sma(df['close'], length=7)  
    df['SMA_long'] = ta.sma(df['close'], length=21)  
    sma10 = ta.sma(df["close"], length=10)
    #ema10_ohlc4 = ta.ema(ta.ohlc4(df["Open"], df["High"], df["Low"], df["Close"]), length=10)
    ta.Strategy('all')   

    # 应用策略并添加信号列到 DataFrame  
    signals = ta.strategy(df, strategy)  
    df = pd.concat([df, signals], axis=1)  

    # 查看结果  
    print(df.tail())
import os
import json
import ccxt
import wind_library
import pandas as pd
import pdb

    #分析涨跌幅
if __name__ == '__main__':
    # 调用函数
    gen = wind_library.generator_ccxt_exchange_kline('gate', 'swap')  # 表格列名：datetime,open,hight,low,volume
    # 创建空的 DataFrame
    result_df = pd.DataFrame(columns=['symbol', 'Natural_growth', 'top_multiple', 'down_multiple'])
    #pdb.set_trace()
    # 循环获取所有 df_kl 和计算结果
    for df_kl in gen:
        natural_growth, top_multiple, down_multiple = wind_library.close_max_multiple(df_kl)
        # 将 df_kl.name 和计算结果添加到 DataFrame 中
        new_row = [df_kl.name.split('/')[0], natural_growth, top_multiple, down_multiple]
        result_df.loc[len(result_df)] = new_row
        		
    # 找到 top_multiple 列的最大值和最小值所对应的 symbol 值和数值
    top_max_row = result_df.loc[result_df['top_multiple'].idxmax()]
    top_min_row = result_df.loc[result_df['top_multiple'].idxmin()]

    # 找到 down_multiple 列的最大值和最小值所对应的 symbol 值和数值
    down_max_row = result_df.loc[result_df['down_multiple'].idxmax()]
    down_min_row = result_df.loc[result_df['down_multiple'].idxmin()]

    # 找到 Natural_growth 列的最大值和最小值所对应的 symbol 值和数值
    growth_max_row = result_df.loc[result_df['Natural_growth'].idxmax()]
    growth_min_row = result_df.loc[result_df['Natural_growth'].idxmin()]

    # 打印结果
    print("Top Multiple Max Symbol:", top_max_row['symbol'], top_max_row['top_multiple'])
    print("Top Multiple Min Symbol:", top_min_row['symbol'], top_min_row['top_multiple'])
    print("Down Multiple Max Symbol:", down_max_row['symbol'], down_max_row['down_multiple'])
    print("Down Multiple Min Symbol:", down_min_row['symbol'], down_min_row['down_multiple'])
    print("Natural Growth Max Symbol:", growth_max_row['symbol'], growth_max_row['Natural_growth'])
    print("Natural Growth Min Symbol:", growth_min_row['symbol'], growth_min_row['Natural_growth'])
    #保存文件
    result_df.to_csv(os.path.join('..', 'data','exchange_kline_analysis_max.csv'), index=False)

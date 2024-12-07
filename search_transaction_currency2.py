import argparse
import pandas as pd
from tqdm import tqdm
import os
import pdb
import datetime
import wind_library     # wind_library是一个包含generator_ccxt_exchange_kline和pandasta_signals函数的用户自定义模块

def simulate_args():
    parser = argparse.ArgumentParser(description='Download kline data from CCXT exchange.')
    parser.add_argument('--exchange', type=str, required=True, help='The exchange name, e.g. gate')
    parser.add_argument('--transaction_type', type=str, required=True, help='The transaction type, e.g. spot or swap')
    parser.add_argument('--kline_period', type=str, required=True, help='The kline period, e.g. 1h')
    parser.add_argument('--limit', type=int, default=100, help='The limit for the number of klines to download')
    # return parser.parse_args(['--exchange', 'gate', '--transaction_type', 'swap', '--kline_period', '1h', '--limit', '100'])   # debug
    return parser.parse_args()

def main(args):
    signal_df = pd.DataFrame()  # 创建空表用于循环插入信号的末5行

    gen = wind_library.generator_ccxt_exchange_kline(
        exchange=args.exchange,
        transaction_type=args.transaction_type,
        kline_period=args.kline_period,
        limit=args.limit
    )

    data_list = []
    for df_kl in tqdm(gen, desc='Processing dataframes'):
        print(df_kl.name, end=', ')
        try:
            df = wind_library.pandasta_signals(df_kl)
        except Exception as e:
            print(f"发生错误：{e}")
            continue

        signal_cols = [col for col in df.columns if col.startswith('signal')]
        signal_sum = df.tail(5)[signal_cols].sum().sum()
        signal_tail = df.tail(5)[signal_cols].to_string(index=False, header=False)
        print(signal_sum)
        print(signal_tail)

        # 将数据添加到列表
        data_list.append({'name': df_kl.name, 'sum': signal_sum,'signal_tail': signal_tail})

    # 将列表转换为DataFrame
    signal_df = pd.DataFrame(data_list)

    # 保存数据到文件
    now = datetime.datetime.now()
    filename = f"{args.exchange}_{args.transaction_type}_{args.kline_period}_{now.strftime('%Y%m%d_%H')}.csv"
    filepath = os.path.join('..', 'data', filename)
    signal_df.to_csv(filepath, index=False)

    return signal_df

if __name__ == '__main__':
    args = simulate_args()
    print(args)
    signal_df = main(args)
    
    # C:\ProgramData\anaconda3\python.exe search_transaction_currency2.py --exchange gate --transaction_type swap --kline_period 15m --limit=100
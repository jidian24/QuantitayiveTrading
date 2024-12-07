import argparse
import pandas as pd
from tqdm import tqdm

# 假设wind_library是一个包含generator_ccxt_exchange_kline和pandasta_signals函数的模块
import wind_library

def main():
    parser = argparse.ArgumentParser(description='Download kline data from CCXT exchange.')
    parser.add_argument('--exchange', type=str, required=True, help='The exchange name, e.g. gate')
    parser.add_argument('--transaction_type', type=str, required=True, help='The transaction type, e.g. spot or swap')
    parser.add_argument('--kline_period', type=str, required=True, help='The kline period, e.g. 1d')
    parser.add_argument('--limit', type=int, default=100, help='The limit for the number of klines to download')

    args = parser.parse_args()

    gen = wind_library.generator_ccxt_exchange_kline(
        exchange=args.exchange,
        transaction_type=args.transaction_type,
        kline_period=args.kline_period,
        limit=args.limit
    )
    # debug
    # gen = wind_library.generator_ccxt_exchange_kline(exchange='gate', transaction_type='swap', kline_period='1h', limit=100)
    for df_kl in tqdm(gen, desc='Processing dataframes'):
        print(df_kl.name, end=', ')
        try:
            df = wind_library.pandasta_signals(df_kl)
        except Exception as e:
            print(f"发生错误：{e}")
            continue

        print(df.tail(5)[[col for col in df.columns if col.startswith('signal')]].sum().sum())  # 信号汇总
        print(df.tail(5)[[col for col in df.columns if col.startswith('signal')]].to_string(index=False, header=False))  # 输出信号列末5行

if __name__ == '__main__':
    main()
# example
# C:\ProgramData\anaconda3\python.exe test2.py --exchange gate --transaction_type swap --kline_period 15m --limit=100
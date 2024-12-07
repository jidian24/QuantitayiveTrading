import ccxt
import wind_library
import pandas as pd  
import pandas_ta as ta  
from multiprocessing import freeze_support  #多线程计算控制
import matplotlib.pyplot as plt
import okx.MarketData as MarketData
import okx.PublicData as PublicData
import okx.Account as Account

api_key = "158ea23a-b647-417f-a0d4-1c2a9a2a4943"
secret_key = "297AAE527D421CF7AE6FA4AA697144B7"
passphrase = "Jidian2$"
flag = "0"  # 实盘:0 , 模拟盘：1
publicDataAPI = PublicData.PublicAPI(flag=flag)
accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
# result = accountAPI.get_instruments(instType="SPOT")
result = accountAPI.get_account_balance()

def get_okx_symbols(instType="SWAP"):
    """list:获取交易产品基础信息"""
    result = publicDataAPI.get_instruments(instType=instType)





marketDataAPI =  MarketData.MarketAPI(flag=flag)


# 获取K线,返回dataframe['datetime', 'open', 'high', 'low', 'close', 'volume']
def get_okx_swap_kline( symbol, transaction_type='swap', bar='1d', limit=None):
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
        klines = marketDataAPI.get_mark_price_candlesticks(instId=symbol, bar= bar, limit=limit)        
        # 获取K线数据: ts 时间戳, open 开盘价, high 最高价, low 最低价, close 收盘价, vol 成交量
        
        # 转换为DataFrame
        df_kl = pd.DataFrame(klines['data'], columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        # df_kl['datetime'] = pd.to_datetime(df_kl['datetime'], unit='ms')
        df_kl.name = symbol
        
        return df_kl
    
    except Exception as e:
        print(f"get_okx_swap_kline发生错误:{e}")
        return None
# df = get_okx_swap_kline('BTC/USDT', '1d', 100)



# 将交易所对象的 urls 属性修改为 customize_urls 中的内容
def get_list_from_okx(instType='SWAP'):
    symbols = marketDataAPI.get_tickers(instType=instType)["data"]           # 获取所有产品行情信息  Get Tickers
    symbols = pd.DataFrame(symbols)# 将字典列表转换为DataFrame
    symbols = symbols.loc[symbols ['instId'].str.contains('-USDT'), ['instId','vol24h']]    #-USDT筛选列 行 _token  
    symbols = symbols.sort_values(["vol24h"],ascending=False)        #volume_24h排降序
    symbols = symbols['instId'].values.tolist()     # get [instrument_id]列
    return (symbols)

list_okx_symbols = get_list_from_okx('SWAP')    # 'AXS-USDT-SWAP'
# print(list_okx_symbols)
df = get_okx_swap_kline('AXS-USDT-SWAP', 'swap', '1H', 100)
print(df)


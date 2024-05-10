
		
import ccxt
#循环获取指定交易所,指定参数的所有USTD交易对k线数据
def ccxt_get_kline(exchange, Transaction_type='spot', kline_period='1d'):
    # 设置交易所
    exchange = getattr(ccxt, exchange)()

    # 设置交易类型和周期
    exchange.load_markets()
    symbol = exchange.symbols[0]
    #if Transaction_type in exchange.markets[symbol]['info']['type']:
    if  exchange.markets[symbol][Transaction_type] and exchange.markets[symbol]['quote']=='USDT':
        klines = exchange.fetch_ohlcv(symbol, kline_period)# 获取 K 线数据
        if klines :              #如果有数据
            df_kl = pd.DataFrame(klines, columns=['datatime','open', 'high','low','close','volume'])    #创建列名称'DataTime','open', 'High','Low','Close','volume'
            df_kl['DataTime'] = pd.to_datetime(df_kl['DataTime'], unit='ms')        #时间格式化
            #print('{}:{}'.format(t_since,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t_since / 1000) )))  # ISO时间格式化
            print('{}\n{}\n{}'.format(df_kl.shape,df_kl.head(1),df_kl.tail(1) ))    #屏幕打印表格首尾行
    df.to_csv(os.path.join('..','data','all_symbols' + '.csv'),index=True)  #表格写入csv文件
    return klines
ccxt_get_kline('gate','spot','5m')
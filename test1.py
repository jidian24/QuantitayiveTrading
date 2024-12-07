import numpy as np
import pandas as pd
import wind_library
import vectorbt as vbt

# 获取Gate.io交易所BTC/USDT的1小时K线数据
ohlcv= wind_library.get_ccxt_exchange_kline('gate', 'BTC/USDT', 'spot', '1h', 200)
price = ohlcv.close
atr = vbt.ATR.run(ohlcv.high,ohlcv.low,price , window=14)
atr.plot()
import numpy as np
import pandas as pd
import vectorbt as vbt
from vectorbt import Portfolio

# 假设你有一个DataFrame 'price'，其中包含了某个资产的历史价格，列名为'Close'
# 这里用随机数据生成一个示例DataFrame
np.random.seed(42)
price = pd.DataFrame({
    'Close': np.random.normal(100, 10, 1000)  # 假设价格数据
})

# 计算ATR指标
# atr_length 是ATR的周期长度，通常设置为14
# atr_multi 是用于生成交易信号的ATR倍数
atr_length = 14
atr_multi = 1.5
atr = vbt.ATR(length=atr_length).run(price['Close'])

# 定义交易信号
# 生成买入信号：当收盘价高于收盘价+ATR倍数时
entries = price['Close'] > price['Close'].shift(1) + atr * atr_multi

# 生成卖出信号：当收盘价低于收盘价-ATR倍数时
exits = price['Close'] < price['Close'].shift(1) - atr * atr_multi

# 应用交易逻辑，确保信号不会连续反转
# entries = vbt.signals.TaSignal(entries, sig lookback=1, max_pos=1).run()
# exits = vbt.signals.TaSignal(exits, sig lookback=1, max_pos=1).run()

# 创建投资组合
# 使用'reverse'参数来反转卖出信号，因为我们想要在价格下跌时卖出
pf = vbt.Portfolio.from_signals(price, entries, exits, fees=0.001, freq='1d', reverse=True)

# 计算投资组合的收益
results = pf.stats()

# 打印结果
print(results)

# 如果你想可视化投资组合的表现
# pf.plot()


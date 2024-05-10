import pandas as pd  
import pandas_ta as ta  
from multiprocessing import freeze_support  #多线程计算控制
import matplotlib.pyplot as plt

if __name__ == '__main__':
    df = pd.read_csv('gate_ADA_USDT.csv')  # 表格列名：datetime,open,hight,low,volume
    momentumStrategy = ta.Strategy(
        name="Custommomentum",
        description="roc",
        ta=[
            {"kind": "roc", "close": "volume", "prefix": "vol"}, #"length": 10 ,
            {"kind": "obv"},
        ]
    )
    df.ta.strategy(momentumStrategy)
    #print(df.tail)
    #"""
    # 绘制 ROC 序列曲线
    ind_size =(22, 6)
    dtitle = 'TradingSignal ' + 'ABC ' + str(len(df))
    # 定义TradingSignalStrategy
    TradingSignalStrategy = ta.Strategy(
        name="TradingSignal",
        description="generate trading signals",
        ta=[
            {"kind": "above_value", "series": df['OBV'], "value": 0},
        ]
    )
    #df.ta.strategy(TradingSignalStrategy)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # 在第一个子图上绘制 vol_ROC_10 曲线
    ax1.plot(df['vol_ROC_10'], color='red', linewidth=1)
    ax1.set_title('vol_R
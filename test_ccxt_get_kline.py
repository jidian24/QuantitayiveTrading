# import wind_library as wlib
# wlib.ccxt_save_kline('gate', 'swap')


# from pycoingecko import CoinGeckoAPI
# cg = CoinGeckoAPI()
# cg.ping()
# cg.get_supported_vs_currencies()
from pycoingecko import CoinGeckoAPI
import matplotlib.pyplot as plt
import time
def price_market_draw(id, time_len):
    cg = CoinGeckoAPI()
    coin_data = cg.get_coin_market_chart_by_id(id, 'usd', time_len) #获得对应代币的价格
    coin_time = []
    coin_price = []
    for i in range(int(time_len)*24): # 由于返回的是小时制，所以总数据等于天数*24
        time_stamp = coin_data['prices'][i][0]/1000  # 返回的是毫秒级时间戳所以除以1000转换成秒级进行处理
        time_local = time.localtime(time_stamp)  # 转换成本地时间
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)  # 进行数据的转换方便观察
        coin_time.append(dt)  # 存入时间队列
        coin_price.append(coin_data['prices'][i][1])  # 存入价格队列
    plt.plot(coin_time, coin_price, linewidth=2)  # 图标绘制，第一个参数是x轴，第二个参数是y轴
    plt.title(id + ' ' + time_len + 'days table', fontsize=14)
    plt.xlabel("time", fontsize=14)
    plt.ylabel("usd", fontsize=14)
    plt.show()
    


if __name__ == '__main__':
    #print(response)

    price_market_draw('bitcoin', '90')
    #调用btc90天的数据形成k线图，第一个参数是代币名字，第二个天数，天数要小于等于90天
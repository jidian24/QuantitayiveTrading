# import ccxt
# import datetime
# import wind_library

# # 列出指定交易所x天数内上市的指定类型的交易对。
# list_symbols = wind_library.ccxt_list_symbols_of_exchange_indays('gate', 'spot', 30)
# print(list_symbols)

import requests
from fake_useragent import UserAgent

hostname = 'https://api.coingecko.com/api/v3/'
command = 'coins/list'
url = hostname + command

headers = {
    'User-Agent': UserAgent().random
}

proxies = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}

def fake_browser_request(url, headers, proxies, timeout=10):
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
        if response.status_code == 200:
            return response.text
        else:
            print(f"请求失败，状态码：{response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"发生错误：{e}")

# 调用函数使用代理服务器连接网址
response = fake_browser_request(url, headers, proxies)
if response:
    print("连接成功！")
else:
    print("连接失败，请检查代理服务器设置和网络状态。")
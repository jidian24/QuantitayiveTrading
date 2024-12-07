import os
import re      
import pdb
import requests
from lxml import etree
import time
import cssselect
import wind_library
import pandas as pd




def get_gate_cryptocurrency_info(info_url):
    retry_count = 0
    while retry_count < 3:
        try:
            response = requests.get(info_url)
            if response.status_code == 200:
                html = response.text
                tree = etree.HTML(html)
                # 在这里编写爬取单个加密货币信息的代码
                sysbol = tree.xpath('//*[@id="__next"]/div[2]/div/div[2]/div/div/section[1]/div/div[1]/div[1]/div/div/div[1]/h1[2]/text()')[1]
                ranking = tree.xpath('//*[@id="__next"]/div[2]/div/div[2]/div/div/section[1]/div/div[1]/div[1]/div/div/div[2]/div/span/text()')[0].split('#')[1]
                market_value = tree.xpath('//*[@id="__next"]/div[2]/div/div[2]/div/div/section[2]/div/div/div[4]/div/div/text()')[0]
                print(sysbol)
                market_value = wind_library.process_money_string(market_value)
                circulation_rate = tree.xpath('//*[@id="__next"]/div[2]/div/div[2]/div/div/section[2]/div/div/div[6]/div/div/text()')
                if circulation_rate: circulation_rate = circulation_rate[0].replace('%', '')
                # describe = tree.xpath('//*[@id="__next"]/div[2]/div/div[2]/div/div/section[3]/div[2]/div[1]/section/section[5]/section[2]/div/div/div/text()')[0]
                about = tree.xpath('//section//h2/div[contains(text(), "关于")]')[0].text.strip()  # 获取标题文本,并去除两端空白
                try:
                    describe = tree.xpath(f'//section//h2/div[contains(text(), "{about}")]/parent::*/following-sibling::div/div/text()')[0]
                except IndexError:
                    describe = None
                try:
                    website = tree.xpath('//div[@class="mantine-vu0c9l"]/a/@href')[0]
                except IndexError:
                    # 如果没有找到匹配的元素,则 xpath() 返回一个空列表,导致 IndexError
                    website = None
                # 并将信息以列表的形式返回
                list_info = [sysbol, ranking, market_value, circulation_rate, describe, website]
                return list_info
                break  # 访问成功,跳出循环
            else:
                # print(f"访问网址 {info_url} 失败,状态码: {response.status_code}")
                retry_count += 1
                time.sleep(1)  # 延迟 1 秒后重试
                return None
        except requests.exceptions.RequestException as e:
            print(f"访问网址 {info_url} 时出现异常: {e}")
            return None
    if retry_count == 3:
        print(f"连续 3 次访问 {info_url} 失败,跳过该网址")
        retry_count += 1
        time.sleep(1)  # 延迟 1 秒后重试

base_url = "https://www.gatexx.club"
page_url = base_url + "/zh/price?page="
xpath_template = '//*[@id="__next"]/div[2]/div/div/div[3]/div[2]/div[1]/table/tbody/tr[{}]/td[1]/div/div/a/@href'

df = pd.DataFrame(columns=['sysbol', 'ranking', 'market_value', 'circulation_rate', 'describe', 'website'])
for ii in range(1, 73):   #get page 1~73   
    url = page_url + str(ii)
    if url == "https://www.gatexx.club/zh/price?page=1": url = "https://www.gatexx.club/zh/price"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            tree = etree.HTML(html)
            for i in range(1, 31):  # 获取每页1~30币种信息url
                xpath = xpath_template.format(i)
                result = tree.xpath(xpath)
                if result:
                    value = result[0]
                    info_url = base_url + value # 构建币种信息url
                    # df_info = ( get_gate_cryptocurrency_info(info_url))
                    df.loc[len(df)] = get_gate_cryptocurrency_info(info_url)# 将get_info内容增加到df表的新的一行
                    # pdb.set_trace()
                else:
                    print(f"第 {ii} 页, XPath {xpath} 未找到匹配的元素")
        else:
            print(f"访问网址 {url} 失败,状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"访问网址 {url} 时出现异常: {e}")
    time.sleep(1)  # 添加延迟,避免过快访问

df.to_csv(os.path.join('..', 'data', 'gate_cryptocurrency_info.csv'), index=False, encoding='utf-8-sig')
print("数据已保存到 gate_cryptocurrency_info.csv 文件中")
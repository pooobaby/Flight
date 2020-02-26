#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright By Eric in 2020

import time
import json
import random
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


# noinspection PyPep8Naming
class Flight(object):
    def __init__(self):
        self.client = MongoClient('localhost', port=27017)
        self.db = self.client.flight
        self.collection = self.db.Flights

        self.code_filename = r'json\city_code.json'

        self.url = 'https://flights.ctrip.com/schedule/'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'}

    def getHtml(self, url):     # 获取网页数据
        reps = requests.get(url=url, headers=self.headers)
        soup = BeautifulSoup(reps.text, 'lxml')
        return soup

    def getCode(self):      # 装载机场代码库
        with open(self.code_filename, 'r', encoding='utf-8') as f:
            city_code = f.read()
        city_code = json.loads(city_code)
        print('-- 城市代码库装载完成，开始下载......')
        return city_code

    def downloadData(self, code, url):  # 下载网页数据并保存到数据库中
        count_n = 0
        soup = self.getHtml(url)
        all_tr = soup.find(id='flt1').find_all('tr')
        for tr in all_tr:
            try:
                all_td = tr.find_all('td')      # 获取所有td的标签
                start_city = all_td[0].text.strip('\n').split('到')[0]   # 出发城市
                end_city = all_td[0].text.strip('\n').split('到')[1]     # 到达城市
                times = [i for i in all_td[1].text.replace(' ', '').split('\n') if i != '']
                start_time = times[0]        # 出发时间
                end_time = times[1]      # 到达时间
                airport = [i for i in all_td[2].text.replace(' ', '').split('\n') if i != '']
                start_airport = airport[0]      # 出发机场
                end_airport = airport[1]        # 到达机场
                company_no = [i for i in all_td[6].text.replace(' ', '').split('\n') if i != '']
                company = company_no[0]     # 航空公司
                flight_no = company_no[1]       # 航班号
                days = '1234567'
                all_i = all_td[4].find_all(class_='none')       # 获取每周不发的班期
                for w in all_i:
                    days = days.replace(w.text, '')         # 将不发的日期从列表中移除
                flight = {
                    'airport_code': code,
                    'start_city': start_city,
                    'end_city': end_city,
                    'start_time': start_time,
                    'end_time': end_time,
                    'start_airport': start_airport,
                    'end_airport': end_airport,
                    'week': days,
                    'company': company,
                    'flight_no': flight_no
                }
                self.collection.insert_one(flight)      # 存储到mongoDB数据库中
                count_n += 1
            except LookupError:      # 捕获映射或序列上使用的键或索引无效时引发的异常的基类
                continue
        return count_n

    def saveData(self, code_dict):  # 分析页数、是否有航班并调用下载函数
        no_list = []
        for code in code_dict:
            count = 0
            city = code_dict[code][0]       # 提取城市名称
            code_low = code.lower()     # 将机场代码转换为小写

            url = self.url + code_low + '-outmap.html'      # 生成第一页的url
            soup = self.getHtml(url)        # 调用getHtml函数获取网页内容
            flights = soup.find(id='flt1')      # 获得id为'flt1'的标签内容

            if 'tr' in str(flights):        # 用’tr'判断是否有航班信息
                whether_one_page = soup.find(class_='schedule_page_list')        # 如果只有一页，查询结果为None
                if whether_one_page is None:
                    print('-- 开始下载从【%s】出发的航班信息，共%d页......' % (city, 1))
                    count_n = self.downloadData(code, url)        # 调用函数下载数据，并返回下载信息数
                    count = count + count_n
                else:
                    pages = int(whether_one_page.find_all('a')[-1].string)      # 获得页码总数
                    print('-- 开始下载从【%s】出发的航班信息，共%d页......' % (city, pages))
                    count_1 = self.downloadData(code, url)        # 先下载第一页的内容
                    print('   第01页下载完成')
                    count = count_1
                    for page_n in range(2, pages + 1):      # 从第2页开始生成新的url
                        url = self.url + code_low + '-outmap-' + str(page_n) + '.html'
                        count_n = self.downloadData(code, url)        # 按页码下载各页
                        time.sleep(random.randint(1, 3))        # 设置随机时间暂停
                        print('   第{:02d}页下载完成'.format(page_n))
                        count = count + count_n
            else:
                print('   没有从【%s】出发的航班信息，继续下一个城市。' % city)
                no_list.append(city)
                continue
            print('   -- 从【%s】出发的航班信息共有%d条，全部下载完成。\n' % (city, count))
            time.sleep(random.randint(1, 3))  # 设置随机时间暂停
        print('下面这些城市没有搜索到航班，请手动添加：\n{}'.format(no_list))

    def modifyCode(self):
        values = [('北京首都国际机场', 'PEK'), ('北京大兴国际机场', 'PKX'), ('上海浦东国际机场', 'PVG'), ('上海虹桥国际机场', 'SHA')]
        for n in values:
            query = {"start_airport": n[0]}
            new_values = {"$set": {"airport_code": n[1]}}
            self.collection.update_many(query, new_values)
        print('北京和上海两个城市的机场代码修改完毕。')


def main():
    flight = Flight()
    code_dict = flight.getCode()
    flight.saveData(code_dict)
    flight.modifyCode()


if __name__ == '__main__':
    main()

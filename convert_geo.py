#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright By Eric in 2020

import json
import requests
import pandas as pd
from tqdm.std import trange
from pymongo import MongoClient


# noinspection PyPep8Naming
class Flight(object):
    def __init__(self):
        self.client = MongoClient('localhost', port=27017)
        self.db = self.client.flight
        self.flight = self.db.Flights
        self.flight_geo = self.db.FlightGeo

        self.key = '高德地图API的key'  # 高德地图API的key
        self.filename = r'json\airport_geo.json'

    def invalidAirport(self):
        """查找库中无效或错误的机场信息，并删除无效或错误记录"""

        flights = pd.DataFrame(self.flight.find({}, {'_id': 0}))    # 去除'_id'列，生成DataFrame
        no_repeat_start = flights.drop_duplicates(subset='start_airport')       # 按出发机场去重
        no_repeat_end = flights.drop_duplicates(subset='end_airport')       # 按到达机场去重
        start = sorted(no_repeat_start.start_airport.tolist())      # 对出发机场排序
        end = sorted(no_repeat_end.end_airport.tolist())        # 对到达机场排序
        invalid_airport = set(end) - set(start)     # 计算到达和出发机场数量的差，生成集合

        print('无效或错误的机场共有{}个：{}'.format(len(invalid_airport), invalid_airport))
        invalid_sum = 0     # 设置需要清理的数据统计初始为0
        row_start = int(flights.shape[0])       # 提取初始DataFrame中所有行数
        for n in invalid_airport:
            invalid_n = flights.loc[flights['end_airport'].isin([n])]       # 按无效或错误机场在DataFrame中查询
            invalid_n = invalid_n.drop_duplicates(subset='start_airport')       # 对查询结果去重
            print('\n-- 无效或错误的机场名称：%s' % n)
            for i in range(invalid_n.shape[0]):     # 遍历无效或错误机场并打印输出
                print('    航班号：{}  出发机场：{}  '.format(invalid_n.iat[i, 9], invalid_n.iat[i, 1]))
                invalid_sum += 1        # 清理的数据+1
            flights = flights[~flights['end_airport'].isin([n])]        # 在DataFrame中删除无效或错误机场的行
        row_end = int(flights.shape[0])     # 提取清理后的DataFrame中所有行数
        row = row_start - row_end       # 得到清理的行数
        print('\n共清理数据%d条, 无效数据已清理完毕，' % row)
        return flights

    def convertGeo(self, address, code):
        url = 'https://restapi.amap.com/v3/geocode/geo?address=' + \
              address + '&key=' + self.key
        reps = requests.get(url)
        geo_data = json.loads(reps.text)
        if geo_data['count'] == '0':  # 过滤不能生成地理位置坐标的数据，返回值为0
            return 0
        pos = geo_data['geocodes'][0]['location'].split(',')
        airport_code = code
        province = geo_data['geocodes'][0]['province']
        city = geo_data['geocodes'][0]['city']
        adcode = geo_data['geocodes'][0]['adcode']
        pos_lon = float(pos[0])
        pos_lat = float(pos[1])
        airport_geo = {
            'airport_code': airport_code,
            'airport': address,
            'province': province,
            'city': city,
            'adcode': adcode,
            'pos_lon': pos_lon,
            'pos_lat': pos_lat
        }       # 生成机场的地理位置字典数据
        return airport_geo

    def saveToDB(self, flights):
        airport_dict = {}  # 定义机场地理数据的字典
        flight_geo = pd.DataFrame(self.flight_geo.find({}, {'_id': 0}))
        if flight_geo.shape[0] == 0:        # 判断数据库是否为空，如果不空则将code转换为列表
            airport_code_list = []
        else:
            airport_code_list = flight_geo.airport_code.tolist()

        code_and_address = flights[['airport_code', 'start_airport']]       # 在清理后的DataFrame中提取出发，到达两列数据
        code_and_address = code_and_address.drop_duplicates(subset='start_airport')     # 按出发机场去重
        address_list = code_and_address.start_airport.tolist()      # 将出发机场转换为列表
        print('开始进行地理位置编码......')
        invalid_address = []        # 定义不能生成地理位置的机场地址列表
        address_num = 0     # 初始化有效生成的数量为0
        for n in trange(len(address_list)):
            code = code_and_address[code_and_address['start_airport'].isin([address_list[n]])].iat[0, 0]    # 提取机场代码
            if code in airport_code_list:        # 判断库中是否含有这个机场的数据
                continue
            else:
                airport_geo = self.convertGeo(address_list[n], code)        # 调用convertGeo生成地理位置
                if airport_geo == 0:        # 如果返回值为0，添加机场地址到不能生成地理位置的列表中
                    invalid_address.append(address_list[n])
                    continue
                else:
                    self.flight_geo.insert_one(airport_geo)     # 返回值如果为0，添加到mongoDB中
                    airport_dict.update({
                        address_list[n]: [airport_geo['pos_lon'], airport_geo['pos_lat']]
                    })      # 添加到地理数据字典中
                    address_num += 1        # 有效生成的数量+1
        print('地理位置编码完成，共生成%d条机场的地理位置数据。' % address_num)

        airport_json = json.dumps(airport_dict, ensure_ascii=False)  # 将地理位置字典转换为json
        with open(self.filename, 'w', encoding='utf-8') as f:  # 存储到json文件中
            f.write(airport_json)
        print('地理位置数据已存入json文件中，文件地址：%s' % self.filename)
        if len(invalid_address) != 0:       # 如果无效的机场地址列表不为空，打印输出
            print('下面的机场没能生成地理位置坐标，请手动添加：\n{}'.format(invalid_address))
        return

    def patch(self, flights):
        """
        invalid_address中的数据是复制不能生成地理坐标的列表
        address中的数据是修改成可以生成地理坐标的列表
        参考地址：https://lbs.amap.com/api/webservice/guide/api/georegeo/
        """
        invalid_address = ['巴彦淖尔天吉泰机场', '沧源佤山机场', '黄山屯溪机场', '吕梁机场', '牡丹江海浪机场',
                           '乌兰浩特机场', '乌兰察布机场', '甘孜格萨尔机场']
        address = ['巴彦淖尔市天吉泰机场', '沧源市机场', '黄山市屯溪机场', '吕梁市机场', '牡丹江市机场',
                   '乌兰浩特市机场', '乌兰察布市机场', '甘孜市格萨尔机场']

        with open(self.filename, 'r', encoding='utf-8') as f:  # 从之前生成的json文件中读取数据并转换成字典
            airport_json = f.read()
        airport_dict = json.loads(airport_json)

        for n in range(len(invalid_address)):
            code = flights[flights['start_airport'].isin([invalid_address[n]])].iat[0, 0]
            airport_geo = self.convertGeo(address[n], code)  # 调用convertGeo生成地理位置
            airport_geo['airport'] = invalid_address[n]     # 用原先的地址替换字典中的值
            self.flight_geo.insert_one(airport_geo)     # 添加到mongoDB中
            airport_dict.update({
                invalid_address[n]: [airport_geo['pos_lon'], airport_geo['pos_lat']]
            })      # 添加到地理数据字典中

        airport_json = json.dumps(airport_dict, ensure_ascii=False)  # 将地理位置字典转换为json
        with open(self.filename, 'w', encoding='utf-8') as f:  # 存储到json文件中
            f.write(airport_json)
        print('地理位置数据已追加写入json文件中，文件地址：%s' % self.filename)


def main():
    flight = Flight()
    flights = flight.invalidAirport()
    flight.saveToDB(flights)
    # flight.patch(flights)


if __name__ == '__main__':
    main()

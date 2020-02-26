#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright By Eric in 2020

import datetime
import pandas as pd
from pymongo import MongoClient


# noinspection PyPep8Naming
class Cleaning(object):
    def __init__(self):
        self.client = MongoClient('localhost', port=27017)
        self.db = self.client.flight
        self.flight = self.db.Flights
        self.flight_geo = self.db.FlightGeo

        self.plane = pd.DataFrame(self.flight.find({}, {'_id': 0}))
        self.geo = pd.DataFrame(self.flight_geo.find({}, {'_id': 0}))

        self.today = int(datetime.datetime.today().strftime("%w"))
        self.weekday = ['Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.', 'Sun.']
        self.city = '沈阳'

    def baseData(self, day):
        plane_day = []
        plane_pd = self.plane[self.plane['week'].str.contains(day)]
        code_list = self.geo.airport_code.tolist()
        for n in range(len(code_list)):
            code = code_list[n]
            aa = plane_pd[plane_pd['airport_code'].isin([code])]
            plane_n = aa.drop_duplicates(subset='flight_no')
            if plane_n.shape[0] == 0:
                continue
            dd = plane_n.iat[0, 1]
            plane_day.append((plane_n.shape[0], dd))
        return plane_day

    def todayData(self):
        # 根据星期，生成当天的数据，做为基础数据使用
        plane_w = self.plane[self.plane['week'].str.contains(str(self.today))]      # 用模糊筛选提取当天数据
        today_out = []  # 定义当天航班的列表
        code_list = self.geo.airport_code.tolist()
        for n in range(len(code_list)):  # 遍历机场地理位置的数据库
            code = code_list[n]  # 提取机场代码
            # 按机场代码在航班库中筛选数量，按航班号去重，获取筛选、去重后的航班数量
            airplane_n = plane_w[plane_w['airport_code'].isin([code])].drop_duplicates(subset='flight_no').shape[0]
            today_out.append((self.geo.iat[n, 1], airplane_n))  # 将出发城市和航班数量加入当天列表
        return today_out

    @staticmethod
    def geoAirport(data):
        # 生成全国机场分布与出港航班数量的地理图数据
        airport_list = data       # 获取当天的列表数据
        plane_sum = 0
        for n in airport_list:      # 遍历列表，统计航班总数
            plane_sum = plane_sum + n[1]
        geo_airport_data = [airport_list, plane_sum]   # 合成画图所需要的数据
        return geo_airport_data

    def mapProvince(self, data):
        # 生成省级机场数量分布的地理图数据
        province = self.geo.loc[:, 'province'].value_counts()       # 提取省省列并统计重复值生成series
        province_sum = len(data)       # 统计所有机场数量
        province_name = province.index.tolist()     # 将series索引生成列表
        province_num = province.tolist()        # 将series值生成列表
        province_list = []
        for n in range(len(province_name)):     # 从两个列表中取值生成数据
            name = province_name[n].replace('维吾尔', '').replace('壮族', '').replace('回族', '')\
                .replace('自治区', '').replace('省', '').replace('市', '')       # 去掉不规范的名称
            province_list.append((name, province_num[n]))
        map_airport_data = [province_list, province_sum]      # 合成画图所需要的数据
        return map_airport_data

    @staticmethod
    def barOutPort(data):
        # 生成按出港航班数量排序的柱状图数据
        reversal = []       # 定义临时的翻转列表
        [reversal.append(item[::-1]) for item in data]      # 将列表中的元组进行翻转
        list_sorted = sorted(reversal, reverse=True)    # 对翻转后的列表排序
        x_data, y_data = [], []
        for n in list_sorted:       # 将机场名称和数量分别生成x,y轴数据
            x_data.append(n[1])
            y_data.append(n[0])
        bar_out_port_data = [[x_data, y_data], sum(y_data), '出港']       # 合成画图所需要的数据
        return bar_out_port_data

    def barInPort(self, data):
        # 生成按出港航班数量排序的柱状图数据
        plane_w = self.plane[self.plane['week'].str.contains(str(self.today))]      # 用模糊筛选提取当天数据
        end_airport_sorted, end_airport, x_data, y_data = [], [], [], []
        for n in data:         # 遍历当天数据，按出发机场查询到达机场并去重后转换成列表
            airplane_n = plane_w[plane_w['start_airport'].isin([n[0]])].drop_duplicates(subset='flight_no')
            airplane_list = airplane_n.end_airport.tolist()
            for i in airplane_list:     # 遍历列表，将到达机场名称加入列表
                end_airport.append(i)
        end_airport_set = set(end_airport)      # 用set方法去重
        for j in end_airport_set:       # 在set集合中遍历并生成x,y轴数据
            end_airport_sorted.append((end_airport.count(j), j))
        end_airport_sorted = sorted(end_airport_sorted, reverse=True)
        for k in end_airport_sorted:
            x_data.append(k[1])
            y_data.append(k[0])
        bar_in_port_data = [[x_data, y_data], sum(y_data), '进港']
        return bar_in_port_data

    def barTime(self, data, in_or_out):
        # 生成每个小时进、出港航班的柱状图数据
        in_or_out_name = '出港' if in_or_out == 'start_airport' else '进港'     # 判断是进港还是出港
        plane_w = self.plane[self.plane['week'].str.contains(str(self.today))]      # 用模糊筛选提取当天数据
        hour_list, x_data, y_data = [], [], []      # 定义小时列表和x,y轴列表
        for n in data:
            times = plane_w[plane_w['start_airport'].isin([n[0]])].drop_duplicates(subset='flight_no')
            if in_or_out == 'start_airport':
                hours = times.start_time.tolist()       # 生成时间的列表
            else:
                hours = times.end_time.tolist()
            for hour in hours:      # 遍历后将小时提取并添加到列表中
                hour_list.append(hour[:2])
        hour_set = set(hour_list)       # 用set方法去重
        hour_set = sorted(hour_set)
        for item in hour_set:       # 在set集合中遍历并生成x,y轴数据
            x_data.append(item)
            y_data.append(hour_list.count(item))
        bar_time_data = [[x_data, y_data], sum(y_data), in_or_out_name]       # 合成画图所需要的数据
        return bar_time_data

    @staticmethod
    def pieTimePart(data):
        # 生成进、出港航班按时间段统计的玫瑰饼图
        part_06_09, part_09_13, part_13_18, part_18_21, part_21_06 = 0, 0, 0, 0, 0
        time_list = []
        for i in range(len(data[0][0])):        # 将原始数据转换成list[(a,b)]格式
            time_list.append((data[0][0][i], data[0][1][i]))
        for n in time_list:     # 按时间段统计航班总数
            if n[0] in ['06', '07', '08']:
                part_06_09 = part_06_09 + int(n[1])
            elif n[0] in ['09', '10', '11', '12']:
                part_09_13 = part_09_13 + int(n[1])
            elif n[0] in ['13', '14', '15', '16', '17']:
                part_13_18 = part_13_18 + int(n[1])
            elif n[0] in ['18', '19', '20']:
                part_18_21 = part_18_21 + int(n[1])
            elif n[0] in ['21', '22', '23', '00', '01', '02', '03', '04', '05']:
                part_21_06 = part_21_06 + int(n[1])
        part_list = [('06时-09时', part_06_09), ('09时-13时', part_09_13), ('13时-18时', part_13_18),
                     ('18时-21时', part_18_21), ('21时-06时', part_21_06)]      # 加入时间段列表中
        bar_part_data = part_list      # 合成画图所需要的数据
        return bar_part_data

    def lineWeekOut(self):
        # 生成本周按天统计的出港航班数据
        x_data = self.weekday
        y_data = []
        day_s = self.weekDays()
        code_list = self.geo.airport_code.tolist()
        for day in range(1, len(x_data)+1):
            sum_day = 0  # 定义周航班列表
            plane_w = self.plane[self.plane['week'].str.contains(str(day))]      # 用模糊筛选提取当天数据
            for n in range(len(code_list)):      # 遍历机场地理位置的数据库
                code = code_list[n]       # 提取机场代码
                # 按机场代码在航班库中筛选数量，按航班号去重，获取筛选、去重后的航班数量
                sum_n = plane_w[plane_w['airport_code'].isin([code])].drop_duplicates(subset='flight_no').shape[0]
                sum_day = sum_day + sum_n
            y_data.append(sum_day)
        bar_week_data = [x_data, y_data, day_s[0], day_s[1]]        # 合成画图所需要的数据
        return bar_week_data

    def barCompanyOut(self):
        # 生成本周航空公司出港数量的数据
        day_s = self.weekDays()     # 获取本周的开始结束日期
        company_sorted, company_list_all, x_data, y_data = [], [], [], []   # 初始化列表
        for day in range(1, 8):     # 从周一至周日，从数据库中获取航空公司全部列表
            plane_w = self.plane[self.plane['week'].str.contains(str(day))]
            plane_w = plane_w.drop_duplicates(subset='flight_no')
            company_day_list = plane_w.company.tolist()
            company_list_all = company_list_all + company_day_list
        company_list_set = set(company_list_all)    # 生成去重的集合
        for n in company_list_set:      # 遍历集合，生成x,y轴数据和排序用的列表
            x_data.append(n)
            y_data.append(company_list_all.count(n))
            company_sorted.append((company_list_all.count(n), n))
        company_sorted = sorted(company_sorted, reverse=True)       # 对列表进行排序取前三名的公司
        company_1 = company_sorted[0][1]
        company_2 = company_sorted[1][1]
        company_3 = company_sorted[2][1]
        bar_company_out = [x_data, y_data, day_s[0], day_s[1], company_1, company_2, company_3]     # 合成画图所需要的数据
        return bar_company_out

    def heatOutPortTime(self, data):
        # 获取每天出港航班时间热力图的数据
        y_data = self.weekday
        hour_list, x_data, value_data = [], [], []  # 定义小时列表和x,y轴列表
        for n in range(1, 25):
            str_n = str(n)
            str_n = str_n.rjust(2, '0')
            x_data.append(str_n)
        for day in range(1, 8):
            plane_w = self.plane[self.plane['week'].str.contains(str(day))]  # 用模糊筛选提取当天数据
            hour_list = []
            for n in data:
                times = plane_w[plane_w['start_airport'].isin([n[0]])].drop_duplicates(subset='flight_no')
                hours = times.start_time.tolist()       # 生成时间的列表
                for hour in hours:      # 遍历后将小时提取并添加到列表中
                    hour_list.append(hour[:2])
            for hour in x_data:       # 在set集合中遍历并生成(x,y,value)数据
                value_data.append([hour, self.weekday[day-1], hour_list.count(hour)])
        heat_out_time_data = [x_data, y_data, value_data]       # 合成画图所需要的数据
        return heat_out_time_data

    def geoLineCity(self):
        # 生成self.city每天出港航班的地理线数据
        plane_city = self.plane[self.plane['start_city'].isin([self.city])]\
            .drop_duplicates(subset='end_airport')       # 按self.city查询，去重
        start_city = plane_city.start_airport.tolist()[0]       # 导出出发机场的名称列表取一个值
        end_city_list = plane_city.end_airport.tolist()         # 导出到达机场的名称列表
        heat_line_city, end_city = [], []
        for n in end_city_list:    # 遍历到达机场列表，生成开始-到达机场数据和到达机场名称列表
            heat_line_city.append((start_city, n))
            end_city.append((n, 5))
        end_city.append((start_city, 5))
        heat_line_city_data = [heat_line_city, end_city]        # 合成画图所需要的数据
        return heat_line_city_data

    @staticmethod
    def weekDays():
        # 获取本周周一至周日日期的函数
        monday, sunday = datetime.date.today(), datetime.date.today()
        one_day = datetime.timedelta(days=1)
        while monday.weekday() != 0:
            monday -= one_day
        while sunday.weekday() != 6:
            sunday += one_day
        monday = '{}年{}月{}日'.format(monday.year, monday.month, monday.day)
        sunday = '{}年{}月{}日'.format(sunday.year, sunday.month, sunday.day)
        weekday = [monday, sunday]
        return weekday

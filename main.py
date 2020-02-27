#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright By Eric in 2020

import time
from painter import Drawing
from cleaner import Cleaning
from pyecharts.charts import Page


class Flight(object):
    def __init__(self):
        self.page = Page(page_title="全国航班信息大数据分析可视化图表")
        self.drawer = Drawing()
        self.cleaner = Cleaning()

    def exec(self):
        today_data = self.cleaner.todayData()                       # 生成当天的基础数据
        geo_airport_data = self.cleaner.geoAirport(today_data)      # 全国机场及出港航班数量分布地理图数据
        map_airport_data = self.cleaner.mapProvince(today_data)     # 省级机场数量分布地理图数据
        bar_out_port_data = self.cleaner.barOutPort(today_data)     # 机场出港航班数量柱状图数据
        bar_in_port_data = self.cleaner.barInPort(today_data)       # 机场进港航班数量柱状图数据
        line_week_out_data = self.cleaner.lineWeekOut()             # 根据周数据生成周内每天出港航班数据--
        bar_company_data = self.cleaner.barCompanyOut()             # 本周航空公司出港航班数据

        bar_out_time_data = self.cleaner.barTime(today_data, 'start_airport')   # 根据当天的基础数据生成出港航班时间数据
        bar_in_time_data = self.cleaner.barTime(today_data, 'end_airport')      # 根据当天的基础数据生成进港航班时间数据
        bar_out_part_data = self.cleaner.pieTimePart(bar_out_time_data)         # 根据出港数据生成出港时段数据
        bar_in_part_data = self.cleaner.pieTimePart(bar_in_time_data)           # 根据进港数据生成进港时段数据
        pie_part_data = [bar_out_part_data, bar_in_part_data,
                         bar_out_time_data[1], bar_in_time_data[1]]             # 将进、出港和总数添加到列表

        heat_out_time_data = self.cleaner.heatOutPortTime(today_data)           # 根据周数据生成每天出港航班时间热力图数据--
        heat_line_city_data = self.cleaner.geoLineCity()                        # 生成城市出港航班热力线图数据

        # ------------------------------------------------------
        self.page.add(self.drawer.geoAirport(geo_airport_data))     # 画全国机场分布与数量图
        self.page.add(self.drawer.mapProvince(map_airport_data))    # 画全国机场省级分布图
        self.page.add(self.drawer.barAirPort(bar_in_port_data))     # 画机场进港航班柱状图
        self.page.add(self.drawer.barAirPort(bar_out_port_data))    # 画机场出港航班柱状图

        self.page.add(self.drawer.lineWeekOut(line_week_out_data))  # 画本周出港航班数量柱状图
        self.page.add(self.drawer.barCompanyOut(bar_company_data))  # 画本周航空公司出港航班柱状图

        self.page.add(self.drawer.barTime(bar_in_time_data))        # 画进港时间的柱状图
        self.page.add(self.drawer.barTime(bar_out_time_data))       # 画出港时间的柱状图

        self.page.add(self.drawer.pieTime(pie_part_data))               # 同时画进、出港时段的玫瑰饼图
        self.page.add(self.drawer.heatOutPortTime(heat_out_time_data))  # 画周每天出港航班时间热力图
        self.page.add(self.drawer.geoLineCity(heat_line_city_data))     # 画城市出港航班热力线图

        self.page.render('flights.html')
        print('数据地图生成完毕，请打开浏览器查看，多谢。')


def main():
    time_start = time.time()
    print('开始清理数据并生成地图，请稍候......')
    flight = Flight()
    flight.exec()
    time_end = time.time()
    print('程序执行时间：{:.04f}'.format(time_end - time_start))


if __name__ == '__main__':
    main()

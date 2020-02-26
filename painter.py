#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright By Eric in 2020


import datetime
from pyecharts import options as opts
from pyecharts.charts import Geo, Map, Pie, Bar, Line, HeatMap
from pyecharts.globals import ChartType


# noinspection PyPep8Naming
class Drawing(object):
    def __init__(self):
        self.today = datetime.datetime.today()
        self.today_ymd = '{}年{}月{}日'.format(self.today.year, self.today.month, self.today.day)
        self.geo_file = r'json\airport_geo.json'

    def geoAirport(self, data)-> Geo:
        # 全国民航机场及出港航班数量分布图
        airport_map = (
            Geo(init_opts=opts.InitOpts(width='1000px', height='500px'))
            .add_schema(maptype="china", zoom=1.2)
            .add_coordinate_json(self.geo_file)      # 从json文件导入坐标值
            .add('', data[0], symbol_size=8, color='#057748')
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))       # 关闭各省名称显示
            .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(type_='color', min_=0, max_=80),
                title_opts=opts.TitleOpts(title='全国民航机场及出港航班数量分布图',
                                          title_textstyle_opts=opts.TextStyleOpts(font_size=20),  # 设置标题大小
                                          subtitle='{}，全国共有{}个机场通航，出港航班{}架次。[数据来源：ctrip.com]'
                                          .format(self.today_ymd, len(data[0]), data[1]))
            )
        )
        return airport_map

    def mapProvince(self, data)-> Map:
        # 全国各省民航机场数量
        Province_map = (
            Map(init_opts=opts.InitOpts(width='1000px', height='500px'))
            .add('机场数量', data[0], "china")
            .set_series_opts(
                label_opts=opts.LabelOpts(is_show=False),       # 关闭各省名称显示
                itemstyle_opts=opts.ItemStyleOpts(color='rgba(255, 255, 255, 0)'))      # 去掉省会的点
            .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(type_='color', min_=0, max_=15),      # 设置最大，最小值
                legend_opts=opts.LegendOpts(is_show=False),     # 不显示图例
                title_opts=opts.TitleOpts(title='全国各省民航机场数量',
                                          title_textstyle_opts=opts.TextStyleOpts(font_size=20),    # 设置标题大小
                                          subtitle='{}，全国共有{}个机场通航，{}，{}，{}是民航机场数量最多的三个。[数据来源：ctrip.com]'
                                          .format(self.today_ymd, data[1],
                                                  data[0][0][0], data[0][1][0], data[0][2][0]))
            )
        )
        return Province_map

    def barAirPort(self, data)-> Bar:
        # 全国民航机场进出港航班数量(TOP 15)
        airport_bar = (
            Bar(init_opts=opts.InitOpts(width='1000px', height='500px'))
            .add_xaxis(data[0][0][:15])
            .add_yaxis("%s" % data[2], data[0][1][:15], color='#425066')
            .set_global_opts(
                legend_opts=opts.LegendOpts(is_show=False),  # 不显示图例
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30)),     # 横坐标标签倾斜
                title_opts=opts.TitleOpts(title='全国民航机场%s航班数量(TOP 15)' % data[2],
                                          title_textstyle_opts=opts.TextStyleOpts(font_size=20),  # 设置标题大小
                                          subtitle='{}，全国共{}航班{}架次，{}，{}，{}是数量最多的三个。[数据来源：ctrip.com]'
                                          .format(self.today_ymd, data[2], data[1],
                                                  data[0][0][0], data[0][0][1], data[0][0][2]))
            )
            .set_series_opts(
                markline_opts=opts.MarkLineOpts(symbol='circle', precision=0,
                                                data=[opts.MarkLineItem(name='平均', type_='average')])   # 平均值线
            )
        )
        return airport_bar

    def barTime(self, data)-> Bar:
        # 进出港航班数量按小时统计
        time_bar = (
            Bar(init_opts=opts.InitOpts(width='1000px', height='500px'))
            .add_xaxis(data[0][0])
            .add_yaxis("{}航班数量".format(data[2]), data[0][1], color='#1685a9')
            .set_series_opts(
                label_opts=opts.LabelOpts(is_show=False),
                markpoint_opts=opts.MarkPointOpts(
                    data=[opts.MarkPointItem(type_="max", name="Max"),
                          opts.MarkPointItem(type_="min", name="Min"), ]),
                markline_opts=opts.MarkLineOpts(symbol='circle', precision=0,
                                                data=[opts.MarkLineItem(name='平均', type_='average')])
            )
            .set_global_opts(
                legend_opts=opts.LegendOpts(is_show=False),  # 不显示图例
                xaxis_opts=opts.AxisOpts(name_rotate=30),       # 【【【X坐标轴标签倾斜，不好使】】】
                title_opts=opts.TitleOpts(title='{}航班数量按小时统计'.format(data[2]),
                                          title_textstyle_opts=opts.TextStyleOpts(font_size=20),  # 设置标题大小
                                          subtitle='{}，全国共{}航班{}架次。[数据来源：ctrip.com]'
                                          .format(self.today_ymd, data[2], data[1]))
            )
        )
        return time_bar

    def pieTime(self, data)-> Pie:
        # 进出港航班数量按时段统计
        time_pie = (
            Pie(init_opts=opts.InitOpts(width='1000px', height='500px'))
            .add("出港", data[0], radius=["30%", "75%"], center=["25%", "50%"], rosetype="radius",
                 label_opts=opts.LabelOpts(is_show=False))
            .add("进港", data[1], radius=["30%", "75%"], center=["75%", "50%"], rosetype="radius",
                 label_opts=opts.LabelOpts(is_show=True))
            .set_global_opts(
                legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"),
                title_opts=opts.TitleOpts(title='进出港航班数量按时段统计',
                                          title_textstyle_opts=opts.TextStyleOpts(font_size=20),  # 设置标题大小
                                          subtitle='{}，全国出港航班共{}架次，进港航班共{}架次。[数据来源：ctrip.com]'
                                          .format(self.today_ymd, data[2], data[3]))
            )
        )
        return time_pie

    @staticmethod
    def barCompanyOut(data)-> Bar:
        # 全国民航机场进出港航班数量(TOP 15)
        company_out_bar = (
            Bar(init_opts=opts.InitOpts(width='1000px', height='500px'))
            .add_xaxis(data[0])
            .add_yaxis("航空公司", data[1], color='#574266')
            .set_global_opts(
                legend_opts=opts.LegendOpts(is_show=False),  # 不显示图例
                datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],     # DataZoom类型
                title_opts=opts.TitleOpts(title='本周航空公司出港航班数量统计',
                                          title_textstyle_opts=opts.TextStyleOpts(font_size=20),  # 设置标题大小
                                          subtitle='{}-{}，本周发送航班最多的航空公司是：{}，{}，{}。[数据来源：ctrip.com]'
                                          .format(data[2], data[3], data[4], data[5], data[6]))
            )
            .set_series_opts(
                label_opts=opts.LabelOpts(is_show=False),  # 不显示标签值
                markpoint_opts=opts.MarkPointOpts(
                    data=[opts.MarkPointItem(type_="max", name="Max"),
                          opts.MarkPointItem(type_="min", name="Min"), ]),      # 最大值，最小值
                markline_opts=opts.MarkLineOpts(symbol='circle', precision=0,
                                                data=[opts.MarkLineItem(name='平均', type_='average')])   # 平均值线
            )
        )
        return company_out_bar

    @staticmethod
    def lineWeekOut(data)-> Line:
        # 本周出港航班数量统计
        week_bar = (
            Line(init_opts=opts.InitOpts(width='1000px', height='500px'))
            .add_xaxis(data[0])
            .add_yaxis("本周", data[1], color='#425066')
            .set_global_opts(
                legend_opts=opts.LegendOpts(is_show=False),  # 不显示图例
                title_opts=opts.TitleOpts(title='本周出港航班数量统计',
                                          title_textstyle_opts=opts.TextStyleOpts(font_size=20),  # 设置标题大小
                                          subtitle='{}-{}，本周共发送航班{}架次。[数据来源：ctrip.com]'
                                          .format(data[2], data[3], sum(data[1]))))
            .set_series_opts(
                markline_opts=opts.MarkLineOpts(symbol='circle', precision=0,
                                                data=[opts.MarkLineItem(name='平均', type_='average')])   # 平均值线
            )
        )
        return week_bar

    def heatOutPortTime(self, data)-> HeatMap:
        out_port_time_heat = (
            HeatMap(init_opts=opts.InitOpts(width='1000px', height='500px'))
            .add_xaxis(data[0])
            .add_yaxis("", data[1], data[2])
            .set_global_opts(
                title_opts=opts.TitleOpts(title='本周出港航班时间热力图',
                                          title_textstyle_opts=opts.TextStyleOpts(font_size=20),
                                          subtitle='{} [数据来源：ctrip.com]'.format(self.today_ymd)),
                visualmap_opts=opts.VisualMapOpts(type_='color', min_=0, max_=6000),
            )
        )
        return out_port_time_heat

    def geoLineCity(self, data)-> Geo:
        count = len(data[0])
        city_Geoline = (
            Geo(init_opts=opts.InitOpts(width='1000px', height='500px'))
            .add_schema(maptype="china", zoom=1.1)
            .add_coordinate_json(self.geo_file)
            .add("", data[1], symbol_size=6, color='#725e82')  # 标记点大小与颜色
            .add("", data[0], type_=ChartType.LINES,
                 linestyle_opts=opts.LineStyleOpts(curve=0.1, width=1, color='#1685a9'),  # 连线的宽度与颜色
                 effect_opts=opts.EffectOpts(is_show=False))  # 关闭涟漪效果
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title="{}民航班机航线图".format(data[0][0][0]),
                                                       subtitle='{}，{}共有直飞全国{}个城市的航班'
                                                       .format(self.today_ymd, data[0][0][0], count))))
        return city_Geoline

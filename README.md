# Flight
根据ctrip.com数据生成的全国航班可视化数据图项目

## 项目须知

* 首先应运行get_data.py，可以自ctrip.com中获取本周全国所有航班的数据；  
    * 会有城市没有搜索到航班，说明本周没有出发航班，可以手动添加；
    * 北京、上海有两个机场，文件中的modifyCode函数用于将这两个城市的机场分开并加入数据库中。
* 其次运行covert_geo.py，生成地理位置坐标：
    * 将清理掉数据库中的无效数据（如北海汽车站等）；
    * 会有一些机场数据无法自动生成地理位置坐标，请手动修改patch函数中的列表参数，并运行此函数。
        * invalid_address中的数据是复制不能生成地理坐标的列表
        * address中的数据是修改成可以生成地理坐标的列表

## 项目文件

* 【main.py】:主文件，实例化对象，调用cleanr.py、painter.py  
* 【cleaner.py】:从数据库中提取数据并清洗数据，生成painter.py画图所需要的数据  
* 【painter.py】:将数据生成可视化的图表并输出flights.html  
* 【get_data.py】:在ctrip.com中按城市获取航班数据  
* 【covert_geo.py】:根据数据生成自定义地理编码经纬度坐标值文件  
* 【flights.html】:输出的项目成果文件  
### .\json
* 【airport_geo.json】从covert_geo.py中输出的机场地理坐标值文件  
* 【city_code.json】ctrip.com的城市代码基础数据文件  

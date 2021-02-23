"""获取地理文件信息"""
import json
from pypinyin import lazy_pinyin
import re
from tqdm import tqdm
from sql_sentences import SQL_User_Country, SQL_IOT_COUNTRY
from request_sidus import SQLHepler
from constants import *
from collections import Counter


# 读取 txt文件
def get_txt_file(filename):
    with open(filename, 'r', encoding='utf8')as f_txt:
        next(f_txt)
        lines = f_txt.readlines()
        country_dict = {}
        for line in lines:
            country = line.split('\t')[0]
            country_name = line.split('\t')[1]
            country_dict[country] = country_name
        return country_dict


# 读取 json文件
def get_json_file(filename):
    with open(filename, 'r', encoding='utf8') as f_json:
        json_data = json.load(f_json)
        return json_data


# 经纬度匹配
def address_match(lat, lng, info=None, numcep=None):
    lat_max = float(lat) * (2 - numcep)
    lat_min = float(lat) * numcep

    lng_max = float(lng) * (2 - numcep)
    lng_min = float(lng) * numcep

    if (lat_min <= float(info.get('lat')) <= lat_max) and (lng_min <= float(info.get('lng')) <= lng_max):
        return info.get('country')


def get_city_equal(json_data):
    city_list = []
    for info in json_data:
        city_list.append(info.get('name'))
    return city_list


# 城市匹配
def city_match(city, lat, lng, city_list, json_data=None, country_dict=None, numcep=None):
    if city in city_list:
        c_list = [i for i, x in enumerate(city_list) if x == city]
        if len(c_list) == 1:
            return country_dict.get(json_data[city_list.index(city)].get('country'))
        else:

            temp_country_list = [json_data[j].get('country') for j in c_list]
            data = Counter(temp_country_list).most_common(1)
            return country_dict.get(data[0][0])

    elif lat and lng:
        # 　不存在遍历数据
        temp_lat = []
        for info in json_data:
            country_simple = address_match(lat, lng, info, numcep)
            if country_simple:
                temp_lat.append(country_simple)

        if temp_lat:
            c = Counter(temp_lat).most_common(1)[0][0]
            data = country_dict.get(c)
            return data

    # 匹配到韩文
    elif re.match(u'[\uAC00-\uD7A3]+', city):
        return country_dict.get('KR')

    # 如果是中文
    elif re.match(u'[\u4e00-\u9fa5]+', city):
        return country_dict.get('CN')


if __name__ == '__main__':
    json_file = 'cities.json'
    json_data = get_json_file(json_file)
    txt_file = 'country.txt'
    country_dict = get_txt_file(txt_file)

    city_list = get_city_equal(json_data)

    for x in range(0, 18000, 500):
        infos = SQLHepler.fetch_all(SQL_User_Country, db_dict=Local_Database_Sidus)
        #
        # 创建本地连接
        for info in tqdm(infos):
            # 解析数据
            country = city_match(info.get('city'), info.get('lat'), info.get('lng'), city_list, json_data=json_data,
                                 country_dict=country_dict, numcep=0.97)
            if country:
                info.update(country=country)
                SQLHepler.sql_execute(SQL_IOT_COUNTRY, info, db_dict=Local_Database_Iot)
    # info = {
    #     'city':'深圳市',
    #     'lat':'',
    #     'lng':''
    # }
    # country = city_match(info.get('city'), info.get('lat'), info.get('lng'), city_list, json_data=json_data,
    #                              country_dict=country_dict, numcep=0.97)
    #
    # print(country)
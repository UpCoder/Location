# -*- coding=utf-8 -*-
import xlrd
import numpy as np
import csv
import os
import cPickle as pickle
from math import sqrt, radians, sin, asin, cos
from Config import Config
def read_csv(excel_path):
    with open(excel_path, 'rb') as f:
        # 采用b的方式处理可以省去很多问题
        count = 0
        reader = csv.reader(f)
        rows = []
        for row in reader:
            rows.append(row)
        return rows
class Tools:
    '''
        封装一些常用的操作
    '''
    @staticmethod
    def MaxMinNormalization(x, Max, Min):
        '''
            对一组向量进行归一化
        :param x:  向量
        :param Max: 最大值
        :param Min: 最小值
        :return:
        '''
        x = (x - Min) / (Max - Min)
        return x
    @staticmethod
    def save_dict(dict_obj, save_path):
        '''
            将dictobj对象持久化
        '''
        with open(save_path, 'wb') as handle:
            pickle.dump(dict_obj, handle, protocol=pickle.HIGHEST_PROTOCOL)
    @staticmethod
    def load_dict(dict_path):
        '''
            将dictobj从磁盘中加载到内存中
        '''
        with open(dict_path, 'rb') as handle:
            dict_obj = pickle.load(handle)
            return dict_obj
    @staticmethod
    def write_csv_file(save_path, lines):
        with open(save_path, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(lines)
    @staticmethod
    def sort_value_dict(dict_obj):
        '''
        对dictobj对象的value进行排序
        :param dict_obj:  dict对象，value是数组类型的数据
        :return: sorted dict
        '''
        for key in dict_obj.keys():
            dict_obj[key].sort()
        return dict_obj

    '''
        计算两个经纬度之间的距离
        返回距离的单位是km
    '''
    @staticmethod
    def haversine(lon1, lat1, lon2, lat2):  # 经度1，纬度1，经度2，纬度2 （十进制度数）
        # 将十进制度数转化为弧度
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine公式
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # 地球平均半径，单位为公里
        return c * r
class Statics:
    '''
        封装对属性的统计操作
    '''
    @staticmethod
    def statics_wifi_id_from_records(records, save_path=None):
        '''
            统计records类型的对象中出现的所有Wi-Fi
        '''
        wifi_ids = []
        for record in records.records:
            for wifi in record.wifis.wifi_arr:
                wifi_ids.append(wifi.id)
        wifi_ids = list(set(wifi_ids))  # 去重复
        if save_path is not None:
            lines = []
            for wifi_id in wifi_ids:
                lines.append(wifi_id+'\n')
            save_file = open(save_path, 'w')
            save_file.writelines(lines)
        return wifi_ids
    @staticmethod
    def statics_wifi_id_from_csvs(csv_paths, save_path=None):
        wifi_ids=[]
        for csv_path in csv_paths:
            rows = read_csv(csv_path)
            for row in rows[1:]:
                wifi_str = row[-1]
                wifis_obj = wifis(wifi_str)
                for wifi_obj in wifis_obj.wifi_arr:
                    wifi_ids.append(wifi_obj.id)
        wifi_ids = list(set(wifi_ids))
        print 'the number of wifi is %d ' % len(wifi_ids)
        if save_path is not None:
            lines = []
            for wifi_id in wifi_ids:
                lines.append(wifi_id+'\n')
            save_file = open(save_path, 'w')
            save_file.writelines(lines)
        return wifi_ids
    @staticmethod
    def statics_mail_shop(csv_path,save_paths):
        '''
            统计商场和商铺的所属关系
        '''
        lines = read_csv(csv_path)
        mail_shop = {} # key是mail的ID value是shop的ID
        shop_mail = {} # key是shop的ID value是mail的ID
        for line in lines[1:]:
            shop_id = line[0]
            mail_id = line[-1]
            if mail_id in mail_shop.keys():
                mail_shop[mail_id].append(shop_id)
            else:
                mail_shop[mail_id] = [shop_id]
            if shop_id in shop_mail.keys():
                print 'Error, shop_id repeat'
            else:
                shop_mail[shop_id] = mail_id
        Tools.save_dict(mail_shop, save_paths[0])
        Tools.save_dict(shop_mail, save_paths[1])
        return mail_shop, shop_mail
    @staticmethod
    def statics_mail_wifi(csv_paths, shop_mail_path, save_path):
        '''
            统计商场和Wi-Fi之间的对应关系
            在这里我们即使用训练集合的数据，又使用测试机的数据来对每个商场构建Wi-Fi的字典
        '''
        lines = read_csv(csv_paths[0])  #先解析train data
        shop_mail_dict = Tools.load_dict(shop_mail_path)
        mail_wifi_dict = {}
        for index, line in enumerate(lines[1:]):
            shop_id = line[1]
            if shop_id not in shop_mail_dict.keys():
                print shop_id
                print "Error, shop id:%s is not in shop mail dict" % shop_id
            mail_id = shop_mail_dict[shop_id]
            wifis_obj = wifis(line[-1])
            wifis_ids = []
            if index%10000 == 0:
                print 'train data index: ', index / 1000
            for wifi_obj in wifis_obj.wifi_arr:
                wifis_ids.append(wifi_obj.id)
            if mail_id in mail_wifi_dict.keys():
                mail_wifi_dict[mail_id].extend(wifis_ids)
            else:
                mail_wifi_dict[mail_id] = []
                mail_wifi_dict[mail_id].extend(wifis_ids)
        print '-'*15, 'finish train data', '-'*15
        lines = read_csv(csv_paths[1])  # 后解析test data
        for line in lines[1:]:
            mail_id = line[2]
            wifis_obj = wifis(line[-1])
            wifis_ids = []
            for wifi_obj in wifis_obj.wifi_arr:
                wifis_ids.append(wifi_obj.id)
            if mail_id in mail_wifi_dict.keys():
                mail_wifi_dict[mail_id].extend(wifis_ids)
            else:
                mail_wifi_dict[mail_id] = []
                mail_wifi_dict[mail_id].extend(wifis_ids)
        for key in mail_wifi_dict.keys():
            mail_wifi_dict[key] = list(set(mail_wifi_dict[key]))
        average_wifi = 0.0
        for key in mail_wifi_dict.keys():
            average_wifi += len(mail_wifi_dict[key])
        print 'the average number of wifi in different mail is %d' % int(average_wifi / len(mail_wifi_dict))
        Tools.save_dict(mail_wifi_dict, save_path)
    '''
        将同一个csv文件中不同的mail的数据存放到不同的csv文件中
        is_training
            true: csv文件是训练csv文件格式
            false: csv文件是测试文件格式
    '''
    @staticmethod
    def statics_different_mail(csv_path, save_dir, is_training, shop_mail_path=None):
        lines = read_csv(csv_path)
        first_line = lines[0]
        mail_records = {}
        if is_training:
            shop_mail_dict = Tools.load_dict(shop_mail_path)
            for line in lines[1:]:
                shop_id = line[1]
                if shop_mail_dict[shop_id] in mail_records.keys():
                    mail_records[shop_mail_dict[shop_id]].append(line)
                else:
                    mail_records[shop_mail_dict[shop_id]] = [line]
        else:
            # 测试数据
            for line in lines[1:]:
                mail_id = line[2]
                if mail_id in mail_records.keys():
                    mail_records[mail_id].append(line)
                else:
                    mail_records[mail_id] = [line]
        # 开始保存
        basename = os.path.basename(csv_path).split('.csv')[0]
        for key in mail_records.keys():
            save_path = os.path.join(
                save_dir, basename+key+'.csv'
            )
            records = mail_records[key]
            records.insert(0, first_line)
            Tools.write_csv_file(save_path, records)
            print save_path, 'have finish saveing!'
    '''
        统计每个Wi-Fi信号源的强度情况
        输出: dict对象，key是Wi-Fi信号源的id，value是输出，代表的是每次出现时的强度
    '''
    @staticmethod
    def statics_wifi_strength(csv_paths, save_path):
        wifi_id_dict = {}
        wifi_strength_dict = {}
        for csv_path in csv_paths:
            lines = read_csv(csv_path)
            for line in lines[1:]:
                record_obj = record(','.join(line))
                for wifi_obj in record_obj.wifis.wifi_arr:
                    wifi_id_dict[wifi_obj.id] = 1
                    wifi_strength_dict[wifi_obj.id] = []
            print len(wifi_strength_dict)
        for csv_path in csv_paths:
            lines = read_csv(csv_path)
            for line in lines[1:]:
                record_obj = record(','.join(line))
                for wifi_obj in record_obj.wifis.wifi_arr:
                    wifi_strength_dict[wifi_obj.id].append(wifi_obj.singal)
            print len(wifi_strength_dict)
        Tools.save_dict(wifi_strength_dict, save_path)

    '''
        统计每个商铺的位置
        :params shop_info_csv 商铺的信息csv
        :params save_dict_path 保存dict的路径
        返回一个dict对象,key是shopid，value是经纬度信息，value[0]是经度，value[1]是纬度
    '''
    @staticmethod
    def statics_shop_longtitude_latitude(shop_info_csv, save_dict_path):
        lines = read_csv(shop_info_csv)
        shop_longitude_latitude_dict = {}
        for line in lines[1:]:
            shop_id = line[0]
            longitude = float(line[2])
            latitude = float(line[3])
            shop_longitude_latitude_dict[shop_id] = [longitude, latitude]
        if save_dict_path is not None:
            Tools.save_dict(shop_longitude_latitude_dict, save_dict_path)
        return shop_longitude_latitude_dict

    '''
        统计记录文件中出现的所有User
        :param csv_path 存有记录的csv文件
        :param is_training 文件是training格式还是val格式
    '''
    @staticmethod
    def statics_user_shown(csv_path, is_training):
        records_obj = records(csv_path, is_training)
        user_set = set()
        for record_obj in records_obj.records:
            user_set.add(record_obj.user_id)
        return list(user_set)
    '''
        统计出现过的移动Wi-Fi的Wi-FiID
        如何判别一个Wi-Fi是不是移动Wi-Fi热点：看同一个Wi-FiID是否在其它商场出现过
        csv_paths 代表的是不同的商场的记录文件，例如['./AB榜测试集-evaluation_publicm_2578.csv']
        save_path 是指找到的每个商场的固定的Wi-Fi的dict的存储路径，key是mailID val是出现过的Wi-FiID
    '''
    @staticmethod
    def statics_notmobile_wifi(csv_paths, save_path):
        wifi_everymail = {}
        for csv_path in csv_paths:
            records_obj = records(csv_path)
            cur_wifi_set = set()
            for record_obj in records_obj.records:
                for wifi_obj in record_obj.wifis.wifi_arr:
                    cur_wifi_set.add(wifi_obj.id)
            basename = os.path.basename(csv_path)
            mailid = basename[basename.find('m_'):basename.find('.csv')]
            if mailid in wifi_everymail.keys():
                wifi_everymail[mailid] = wifi_everymail[mailid] | cur_wifi_set
            else:
                wifi_everymail[mailid] = cur_wifi_set
        print 'We have find the set of wifi shown in every mail'
        # So far, 我们已经找到了每个商场在训练集和测试集出现的所有Wi-Fi的ID集合
        notmobilewifi_everymail = {}    # 找出每个商场的固定Wi-Fi
        for mailid in wifi_everymail.keys():
            cur_wifi_set = wifi_everymail[mailid]
            for mailid1 in wifi_everymail.keys():
                if mailid1 == mailid:
                    continue
                # 排除在其它商场出现的Wi-Fi
                cur_wifi_set = cur_wifi_set - (cur_wifi_set & wifi_everymail[mailid1])
            notmobilewifi_everymail[mailid] = cur_wifi_set
            print 'had find the not mobile wifi set in ', mailid, \
                'the size of all shown wifi is ', len(wifi_everymail[mailid]), \
                'the size of not mobile wifi is', len(cur_wifi_set)
        Tools.save_dict(
            notmobilewifi_everymail,
            save_path
        )
class wifi_info:
    '''
        封装了一个Wi-Fi信号源
    '''
    def __init__(self, string):
        self.info_str = string
        splits_arr = string.split('|')
        self.id = splits_arr[0]
        self.singal = int(splits_arr[1])
        self.flag = bool(splits_arr[2])
    def __str__(self):
        return "%s, %d, %s" % (self.id, self.singal, str(self.flag))
class wifis:
    '''
        代表的是一条记录接受到的Wi-Fi信号源，可以一次接受到多个Wi-Fi信号源
    '''
    def __init__(self, string):
        self.infos_str = string
        splits_arr = self.infos_str.split(';')
        self.wifi_arr = []
        for split in splits_arr:
            self.wifi_arr.append(
                wifi_info(split)
            )
    def __str__(self):
        res = ''
        for wifi in self.wifi_arr:
            res += str(wifi) +'\n'
        return res
class record:
    '''
        代表一条记录
    '''
    def __init__(self, string, is_training=True):
        # if is_training:
        # self.string = string
        # splits_arr = self.string.split(',')
        # self.user_id = splits_arr[0]
        # self.shop_id = splits_arr[1]
        # self.time_stamp = splits_arr[2]
        # self.longitude = splits_arr[3]
        # self.latitude = splits_arr[4]
        # self.wifis = wifis(splits_arr[-1])
        if is_training:
            self.string = string
            splits_arr = self.string.split(',')
            self.user_id = splits_arr[0]
            self.shop_id = splits_arr[1]
            self.time_stamp = splits_arr[2]
            self.longitude = splits_arr[3]
            self.latitude = splits_arr[4]
            self.wifis = wifis(splits_arr[-1])
        else:
            self.string = string
            splits_arr = self.string.split(',')
            self.row_id = splits_arr[0]
            self.user_id = splits_arr[1]
            self.mail_id = splits_arr[2]
            self.time_stamp = splits_arr[3]
            self.longitude = splits_arr[4]
            self.latitude = splits_arr[5]
            self.wifis = wifis(splits_arr[-1])
class records:
    '''
        代表一个集合的数据
    '''
    def __init__(self,csv_path, is_training=True):
        rows = read_csv(csv_path)
        self.records = []
        for row in rows[1:]:
            self.records.append(record(','.join(row), is_training))
        print 'the number of record is %d, from file is %s' % (len(self.records), csv_path)

if __name__ == '__main__':
    # Statics.statics_shop_longtitude_latitude(
    #     shop_info_csv=Config.shop_data_path,
    #     save_dict_path=os.path.join(Config.data_dir, 'shop_longitude_latitude.txt')
    # )
    # from glob import glob
    # csv_paths = glob(os.path.join(Config.data_dir, '*m_*.csv'))
    # Statics.statics_notmobile_wifi(
    #     csv_paths,
    #     os.path.join(Config.data_dir, 'mail_notMobileWifi.txt')
    # )
    Statics.statics_different_mail(
        os.path.join(Config.data_dir, 'show', 'AB榜测试集-evaluation_public_not_shown.csv'),
        os.path.join(Config.data_dir, 'show', 'not_shown'),
        is_training=False
    )


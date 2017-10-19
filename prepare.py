# -*- coding=utf-8 -*-
import xlrd
import numpy as np
import csv
import os
import cPickle as pickle
data_dir = '/home/give/PycharmProjects/Location/data/data'
shop_data_path=os.path.join(data_dir, '训练数据-ccf_first_round_shop_info.csv')
train_user_data_path=os.path.join(data_dir, '训练数据-ccf_first_round_user_shop_behavior.csv')
val_user_data_path = os.path.join(data_dir, 'AB榜测试集-evaluation_public.csv')
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
    def __init__(self, string):
        self.string = string
        splits_arr = self.string.split(',')
        self.user_id = splits_arr[0]
        self.shop_id = splits_arr[1]
        self.time_stamp = splits_arr[2]
        self.longitude = splits_arr[3]
        self.latitude = splits_arr[4]
        self.wifis = wifis(splits_arr[-1])
class records:
    '''
        代表一个集合的数据
    '''
    def __init__(self,csv_path):
        rows = read_csv(csv_path)
        self.records = []
        for row in rows[1:]:
            self.records.append(record(','.join(row)))
        print 'the number of record is %d, from file is %s' % (len(self.records), csv_path)

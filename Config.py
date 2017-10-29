# -*- coding=utf-8 -*-


import os
class Config:
    data_dir = '/home/give/PycharmProjects/Location/data/data'
    shop_data_path = os.path.join(data_dir, '训练数据-ccf_first_round_shop_info.csv')
    train_user_data_path = os.path.join(data_dir, '训练数据-ccf_first_round_user_shop_behavior.csv')
    val_user_data_path = os.path.join(data_dir, 'AB榜测试集-evaluation_public.csv')
    mail_shop_txt_path = os.path.join(data_dir, 'mail_shop.txt')
    shop_mail_txt_path = os.path.join(data_dir, 'shop_mail.txt')
    mail_wifi_txt_path = os.path.join(data_dir, 'mail_wifi.txt')
    mail_notMobileWifi_txt_path = os.path.join(data_dir, 'mail_notMobileWifi.txt')
    shop_longitude_latitude_txt_path = os.path.join(data_dir, 'shop_longitude_latitude.txt')
    wifi_strength_txt_path = os.path.join(data_dir, 'wifi_strength.txt')
